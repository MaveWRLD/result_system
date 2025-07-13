import json
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Prefetch, Q
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from .models import (  # SubmittedResult,; SubmittedResultScore,
    Assessment,
    Course,
    Enrollment,
    Result,
    ResultModificationLog,
)
from .permissions import (
    CanCreateResult,
    IsResultAssessmentDraft,
    IsResultDraft,
    ViewResultRoles,
)
from .serializers import (  # SubmitResultSerializer,; SubmittedResultScoreSerializer,; SubmittedResultSerializer,
    AssessmentSerializer,
    CourseSerializer,
    ResultModificationLogSerializer,
    ResultSerializer,
)

User = get_user_model()


class CourseViewSet(ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        return Course.objects.filter(lecturer_id=self.request.user.id).order_by("id")

    def get_serializer_context(self):
        return {"lecturer_id": self.request.user.id}


class ResultViewSet(ModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [IsResultDraft, CanCreateResult]

    @action(detail=True, methods=["post", "get"])
    def submit(self, request, course_pk=None, pk=None):
        result = self.get_object()
        if result.course.lecturer.id != request.user.id:
            return Response(
                {"detail": "You are not authorized to perform this action"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if result.status != "D":
            return Response(
                {
                    "detail": f"Can not submit result in {result.get_status_display()} status"
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        result.status = "P_D"
        result.submitted_at = timezone.now()
        result.save()
        return Response(
            {
                "statue": result.status,
                "submitted_at": result.submitted_at,
                "message": "Result submitted successfully for department for approval",
            },
            status=status.HTTP_200_OK,
        )

    def get_queryset(self):
        user = self.request.user

        return Result.objects.select_related("course__lecturer").filter(
            course__lecturer=user.id, course_id=self.kwargs["course_pk"], status="D"
        )

    def get_object(self):
        obj = super().get_object()
        if obj.status != "D":
            raise Http404("Result has been submitted")
        return obj

    def get_serializer_context(self):
        return {"course_id": self.kwargs["course_pk"]}


class ViewResultViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [ViewResultRoles]

    def get_queryset(self):
        user = self.request.user
        dro = user.is_dro
        fro = user.is_fro
        co = user.is_co
        lecturer = user.is_lecturer
        if dro:
            return Result.objects.filter(
                course__program__department=user.profiles.department,
                status="P_D",
            )
        elif fro:
            return Result.objects.filter(
                course__program__department__faculty=user.profiles.department.faculty,
                status="P_F",
            )
        elif lecturer:
            return Result.objects.filter(
                course__lecturer=user.id,
            )
        elif co:
            return Result.objects.filter(status="A")


class AssessmentViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    serializer_class = AssessmentSerializer
    permission_classes = [IsResultAssessmentDraft]

    def get_queryset(self):
        result_id = self.kwargs.get("result_pk")
        user = self.request.user
        dro = user.is_dro
        fro = user.is_fro
        co = user.is_co
        lecturer = user.is_lecturer
        if dro:
            return Assessment.objects.filter(
                result__status="P_D",
                result__course__program__department=user.profiles.department,
                result_id=self.kwargs.get("result_pk"),
            )
        elif fro:
            return Assessment.objects.filter(
                result__status="P_F",
                result__course__program__department__faculty=user.profiles.department.faculty,
                result_id=self.kwargs.get("result_pk"),
            )
        elif co:
            return Assessment.objects.filter(
                result__status="A", result_id=self.kwargs.get("result_pk")
            )
        elif lecturer:
            return Assessment.objects.filter(
                result__course__lecturer=user.id, result_id=self.kwargs.get("result_pk")
            )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {
                "result": getattr(self, "_cached_result", None),
                "result_id": self.kwargs.get("result_pk"),
            }
        )
        return context


# class SubmittedResultViewSet(
#    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
# ):
#    queryset = SubmittedResult.objects.all()
#    permission_classes = [DjangoModelPermissions]
#
#    def get_queryset(self):
#        user = self.request.user
#        dro_role = user.is_dro
#        fro_role = user.is_fro
#        co_role = user.is_co
#        lecturer_roles = user.is_lecturer
#        if dro_role:
#            return SubmittedResult.objects.filter(
#                lecturer__profiles__department=user.profiles.department,
#                result_status="P_D",
#            )
#        if fro_role:
#            return SubmittedResult.objects.filter(
#                lecturer__profiles__department__faculty=user.profiles.department.faculty,
#                result_status="P_F",
#            )
#        if co_role:
#            return SubmittedResult.objects.filter(result_status="A")
#        elif lecturer_roles:
#            return SubmittedResult.objects.filter(lecturer=user.id)
#
#    def get_serializer_class(self):
#        return SubmittedResultSerializer
#
#    def get_serializer_context(self):
#        return {"lecturer_id": self.request.user.id}
#

# class SubmittedResultScoreViewSet(
#    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
# ):
#    serializer_class = SubmittedResultScoreSerializer
#    permission_classes = [DjangoModelPermissions]
#
#    def get_queryset(self):
#        submitted_result_id = self.kwargs["submitted_result_pk"]
#        return SubmittedResultScore.objects.filter(
#            submitted_result_id=submitted_result_id
#        ).order_by("student_id")
#
#    def decimal_to_float(self, value):
#        """Convert Decimal to float for JSON serialization"""
#        if isinstance(value, Decimal):
#            return float(value)
#        return value
#
#    def get_changes(self, instance, validated_data):
#        """Identify changed fields and return old/new values"""
#        changes = {}
#        for field, new_value in validated_data.items():
#            # Skip read-only fields
#            if field in self.serializer_class.Meta.read_only_fields:
#                continue
#
#            old_value = getattr(instance, field)
#
#            # Convert Decimals for proper comparison
#            if isinstance(old_value, Decimal) or isinstance(new_value, Decimal):
#                old_value = self.decimal_to_float(old_value)
#                new_value = self.decimal_to_float(new_value)
#
#            if old_value != new_value:
#                changes[field] = {"old": old_value, "new": new_value}
#
#        return changes
#
#    @transaction.atomic
#    def update(self, request, *args, **kwargs):
#        instance = self.get_object()
#        serializer = self.get_serializer(instance, data=request.data, partial=True)
#        serializer.is_valid(raise_exception=True)
#
#        # Identify changes before saving
#        changes = self.get_changes(instance, serializer.validated_data)
#
#        # Require reason if changes exist
#        if changes:
#            reason = request.data.get("correction_reason")
#            if not reason:
#                return Response(
#                    {"detail": "Correction reason is required when modifying scores"},
#                    status=status.HTTP_400_BAD_REQUEST,
#                )
#            self.perform_update(serializer)
#
#            # Create modification log with only changed fields
#            ResultModificationLog.objects.create(
#                submitted_result_score=instance,
#                modified_by=request.user,
#                old_data={
#                    field: self.decimal_to_float(change["old"])
#                    for field, change in changes.items()
#                },
#                new_data={
#                    field: self.decimal_to_float(change["new"])
#                    for field, change in changes.items()
#                },
#                reason=reason,
#            )
#
#            # Return updated data with 200 OK even if there were no significant changes
#            return Response(serializer.data, status=status.HTTP_200_OK)
#
#        # No changes - still return data with 200 OK, just indicating no updates
#        return Response(
#            {"detail": "No changes were made."},
#            status=status.HTTP_200_OK,
#        )
#
#    # Bulk update for multiple scores
#    @action(detail=False, methods=["patch"], url_path="bulk-update")
#    def bulk_update(self, request):
#        updates = request.data.get("scores", [])
#        reason = request.data.get("correction_reason")
#
#        if not isinstance(updates, list):
#            return Response(
#                {"detail": "Expected list of score updates"},
#                status=status.HTTP_400_BAD_REQUEST,
#            )
#
#        if not reason:
#            return Response(
#                {"detail": "Correction reason is required for bulk updates"},
#                status=status.HTTP_400_BAD_REQUEST,
#            )
#
#        results = []
#        logs = []
#
#        with transaction.atomic():
#            for item in updates:
#                try:
#                    instance = SubmittedResultScore.objects.get(id=item["id"])
#                    serializer = self.get_serializer(instance, data=item, partial=True)
#                    serializer.is_valid(raise_exception=True)
#
#                    # Track changes per score
#                    changes = self.get_changes(instance, serializer.validated_data)
#                    if changes:
#                        serializer.save()
#
#                        logs.append(
#                            ResultModificationLog(
#                                submitted_result_score=instance,
#                                modified_by=request.user,
#                                old_data={
#                                    f: self.decimal_to_float(c["old"])
#                                    for f, c in changes.items()
#                                },
#                                new_data={
#                                    f: self.decimal_to_float(c["new"])
#                                    for f, c in changes.items()
#                                },
#                                reason=reason,
#                            )
#                        )
#
#                        results.append(
#                            {
#                                "id": instance.id,
#                                "status": "updated",
#                                "changes": list(changes.keys()),
#                            }
#                        )
#                    else:
#                        results.append({"id": instance.id, "status": "no_changes"})
#                except SubmittedResultScore.DoesNotExist:
#                    results.append({"id": item.get("id"), "status": "not_found"})
#                    continue
#                except KeyError:
#                    results.append({"id": item.get("id"), "status": "invalid_data"})
#                    continue
#
#            # Bulk create logs
#            if logs:
#                ResultModificationLog.objects.bulk_create(logs)
#
#        return Response(results, status=status.HTTP_200_OK)


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
