import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Prefetch
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from .models import (
    Assessment,
    Course,
    Enrollment,
    Result,
    ResultModificationLog,
    SubmittedResult,
    SubmittedResultScore,
)
from .permissions import IsAdminOrReadOnly
from .serializers import (
    AssessmentSerializer,
    CourseSerializer,
    ResultModificationLogSerializer,
    ResultSerializer,
    SubmitResultSerializer,
    SubmittedResultScoreSerializer,
    SubmittedResultSerializer,
)

User = get_user_model()


class CourseViewSet(ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Course.objects.filter(lecturer_id=self.request.user.id).order_by("id")

    # def get_queryset(self):
    #    print(Course.objects.all())
    #    return Course.objects.all()

    def get_serializer_context(self):
        return {"lecturer_id": self.request.user.id}


class ResultViewSet(ModelViewSet):
    queryset = Result.objects.select_related("course").all()
    serializer_class = ResultSerializer

    @action(detail=True, methods=["post", "get"])
    def submit(self, request, course_pk=None, pk=None):
        serializer = SubmitResultSerializer(
            data=request.data,
            context={
                "lecturer_id": request.user.id,
                "result_id": self.kwargs["pk"],
                "course_id": self.kwargs["course_pk"],
            },
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get_queryset(self):
        return (
            Result.objects.filter(course_id=self.kwargs["course_pk"])
            .select_related("course")
            .prefetch_related("course__enrolled_course__student")
        )

    def get_serializer_context(self):
        return {"course_id": self.kwargs["course_pk"]}


class AssessmentViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = AssessmentSerializer

    def get_queryset(self):
        result_id = self.kwargs.get("result_pk")
        queryset = Assessment.objects.filter(result_id=result_id)\
            .select_related('result__course', 'student')\
            .prefetch_related(
                Prefetch('student__enrolled_student',
                       queryset=Enrollment.objects.select_related('course'))
            )
        
        # Cache the result object for serializer context
        if queryset.exists():
            result = queryset.first().result
            result.prefetched_assessments = queryset
            self._cached_result = result
        else:
            self._cached_result = Result.objects.select_related('course').get(pk=result_id)
            
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({
            "result": getattr(self, '_cached_result', None),
            "result_id": self.kwargs.get("result_pk")
        })
        return context


class SubmittedResultViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = SubmittedResult.objects.all()
    permission_classes = [DjangoModelPermissions]

    def get_queryset(self):
        user = self.request.user
        dro_role = user.is_dro
        fro_role = user.is_fro
        co_role = user.is_co
        lecturer_roles = user.is_lecturer
        if dro_role:
            return SubmittedResult.objects.filter(
                lecturer__profiles__department=user.profiles.department,
                result_status="P_D",
            )
        if fro_role:
            return SubmittedResult.objects.filter(
                lecturer__profiles__department__faculty=user.profiles.department.faculty,
                result_status="P_F",
            )
        if co_role:
            return SubmittedResult.objects.filter(result_status="A")
        elif lecturer_roles:
            return SubmittedResult.objects.filter(lecturer=user.id)

    def get_serializer_class(self):
        return SubmittedResultSerializer

    def get_serializer_context(self):
        return {"lecturer_id": self.request.user.id}


class SubmittedResultScoreViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = SubmittedResultScore.objects.all().order_by("student_id")
    serializer_class = SubmittedResultScoreSerializer
    permission_classes = [DjangoModelPermissions]

    def decimal_to_float(self, value):
        """Convert Decimal to float for JSON serialization"""
        if isinstance(value, Decimal):
            return float(value)
        return value

    def get_changes(self, instance, validated_data):
        """Identify changed fields and return old/new values"""
        changes = {}
        for field, new_value in validated_data.items():
            # Skip read-only fields
            if field in self.serializer_class.Meta.read_only_fields:
                continue

            old_value = getattr(instance, field)

            # Convert Decimals for proper comparison
            if isinstance(old_value, Decimal) or isinstance(new_value, Decimal):
                old_value = self.decimal_to_float(old_value)
                new_value = self.decimal_to_float(new_value)

            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}

        return changes

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Identify changes before saving
        changes = self.get_changes(instance, serializer.validated_data)

        # Require reason if changes exist
        if changes:
            reason = request.data.get("correction_reason")
            if not reason:
                return Response(
                    {"detail": "Correction reason is required when modifying scores"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            self.perform_update(serializer)

            # Create modification log with only changed fields
            ResultModificationLog.objects.create(
                submitted_result_score=instance,
                modified_by=request.user,
                old_data={
                    field: self.decimal_to_float(change["old"])
                    for field, change in changes.items()
                },
                new_data={
                    field: self.decimal_to_float(change["new"])
                    for field, change in changes.items()
                },
                reason=reason,
            )

            # Return updated data with 200 OK even if there were no significant changes
            return Response(serializer.data, status=status.HTTP_200_OK)

        # No changes - still return data with 200 OK, just indicating no updates
        return Response(
            {"detail": "No changes were made."},
            status=status.HTTP_200_OK,
        )

    # Bulk update for multiple scores
    @action(detail=False, methods=["patch"], url_path="bulk-update")
    def bulk_update(self, request):
        updates = request.data.get("scores", [])
        reason = request.data.get("correction_reason")

        if not isinstance(updates, list):
            return Response(
                {"detail": "Expected list of score updates"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not reason:
            return Response(
                {"detail": "Correction reason is required for bulk updates"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        logs = []

        with transaction.atomic():
            for item in updates:
                try:
                    instance = SubmittedResultScore.objects.get(id=item["id"])
                    serializer = self.get_serializer(instance, data=item, partial=True)
                    serializer.is_valid(raise_exception=True)

                    # Track changes per score
                    changes = self.get_changes(instance, serializer.validated_data)
                    if changes:
                        serializer.save()

                        logs.append(
                            ResultModificationLog(
                                submitted_result_score=instance,
                                modified_by=request.user,
                                old_data={
                                    f: self.decimal_to_float(c["old"])
                                    for f, c in changes.items()
                                },
                                new_data={
                                    f: self.decimal_to_float(c["new"])
                                    for f, c in changes.items()
                                },
                                reason=reason,
                            )
                        )

                        results.append(
                            {
                                "id": instance.id,
                                "status": "updated",
                                "changes": list(changes.keys()),
                            }
                        )
                    else:
                        results.append({"id": instance.id, "status": "no_changes"})
                except SubmittedResultScore.DoesNotExist:
                    results.append({"id": item.get("id"), "status": "not_found"})
                    continue
                except KeyError:
                    results.append({"id": item.get("id"), "status": "invalid_data"})
                    continue

            # Bulk create logs
            if logs:
                ResultModificationLog.objects.bulk_create(logs)

        return Response(results, status=status.HTTP_200_OK)


class ResultModificationLogViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ResultModificationLogSerializer
    queryset = ResultModificationLog.objects.all().select_related(
        "modified_by", "submitted_result_score", "submitted_result_score__student"
    )

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = [
    #    'submitted_result_score__id',
    #    'modified_by__id',
    #    'submitted_result_score__student__id'
    # ]


# Create your views here.
