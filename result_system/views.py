import base64
import io
import json
from decimal import Decimal

import pyotp
import qrcode
from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.db.models import Prefetch, Q
from django.urls import path
from django.utils import timezone
from djoser.views import TokenCreateView
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken

from core.models import User

from .models import (  # SubmittedResult,; SubmittedResultScore,
    Assessment,
    CASlotMax,
    Course,
    Enrollment,
    Result,
    ResultModificationLog,
)
from .permissions import (
    CanCreateResult,
    CanEditResultAssessment,
    IsResultDraft,
    ViewResultRoles,
)
from .serializers import (  # SubmitResultSerializer,; SubmittedResultScoreSerializer,; SubmittedResultSerializer,
    AssessmentSerializer,
    CASlotMaxSerializer,
    CourseSerializer,
    ResultModificationLogSerializer,
    ResultSerializer,
)

User = get_user_model()


class CourseViewSet(ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    # permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.is_dro:
            return Course.objects.filter(
                lecturer__is_active=False, program__department=user.profile.department
            ).order_by("id")
        return Course.objects.filter(lecturer_id=self.request.user.id).order_by("id")

    def get_serializer_context(self):
        return {"lecturer_id": self.request.user.id}


class ResultViewSet(ModelViewSet):
    serializer_class = ResultSerializer
    permission_classes = [IsResultDraft, CanCreateResult]

    @action(detail=True, methods=["put", "get"])
    def submit(self, request, course_pk=None, pk=None):
        result = self.get_object()
        user = self.request.user
        if (
            not result.course.lecturer.is_active and user.is_dro
        ) or result.course.lecturer.id == request.user.id:
            result.status = "P_D"
            result.updated_by = self.request.user
            result.submitted_at = timezone.now()
            result.save()
            return Response(
                {
                    "status": result.status,
                    "submitted_at": result.submitted_at,
                    "message": "Result submitted successfully for department for approval",
                },
                status=status.HTTP_200_OK,
            )
        elif result.course.lecturer.id != request.user.id:
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

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
        return super().perform_update(serializer)

    def get_queryset(self):
        user = self.request.user

        if user.is_dro:
            return Result.objects.select_related("course__program__department").filter(
                course__lecturer__is_active=False,
                course__program__department=user.profile.department,
                course_id=self.kwargs["course_pk"],
                status="D",
            )
        return Result.objects.select_related("course").filter(
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

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def get_queryset(self):
        user = self.request.user
        dro = user.is_dro
        fro = user.is_fro
        co = user.is_co
        lecturer = user.is_lecturer

        if dro:
            return Result.objects.filter(
                Q(course__lecturer__is_active=False) | Q(status="P_D"),
                course__program__department=user.profile.department,
            ).exclude(status="D")
        elif fro:
            return Result.objects.filter(
                course__program__department__faculty=user.profile.department.faculty,
                status="P_F",
            )
        elif lecturer:
            return Result.objects.filter(course__lecturer=user.id).exclude(
                status__in=("D")
            )
        elif co:
            return Result.objects.filter(status="A")


class AssessmentViewSet(
    ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet
):
    serializer_class = AssessmentSerializer
    permission_classes = [CanEditResultAssessment]

    def get_queryset(self):
        #        read_only_fields = ("id", "submitted_result_id", "student_id")
        user = self.request.user
        dro = user.is_dro
        fro = user.is_fro
        co = user.is_co
        lecturer = user.is_lecturer
        course = Course.objects.get(results=self.kwargs.get("result_pk"))

        route_name = self.request.resolver_match.url_name
        print(course.results.status)
        print(route_name)

        if (
            dro
            and course.results.status == "D"
            and route_name in ["result-assessment-list", "result-assessment-detail"]
        ):
            return Assessment.objects.filter(
                Q(result__course__lecturer__is_active=False) & Q(result__status="D")
                | Q(result__status="P_D"),
                result__course__program__department=user.profile.department,
                result_id=self.kwargs.get("result_pk"),
            )
        elif (
            dro
            and course.results.status != "D"
            and route_name
            in ["submitted-result-score-list", "submitted-result-score-detail"]
        ):
            return Assessment.objects.filter(
                Q(result__course__lecturer__is_active=False) | Q(result__status="P_D"),
                result__course__program__department=user.profile.department,
                result_id=self.kwargs.get("result_pk"),
            )
        elif fro:
            return Assessment.objects.filter(
                result__status="P_F",
                result__course__program__department__faculty=user.profile.department.faculty,
                result_id=self.kwargs.get("result_pk"),
            )
        elif co:
            return Assessment.objects.filter(
                result__status="A", result_id=self.kwargs.get("result_pk")
            )
        elif lecturer and route_name in [
            "result-assessment-list",
            "result-assessment-detail",
        ]:
            return Assessment.objects.filter(
                result__status="D",
                result__course__lecturer=user.id,
                result_id=self.kwargs.get("result_pk"),
            )
        elif lecturer and route_name in [
            "submitted-result-score-list",
            "submitted-result-score-detail",
        ]:
            return Assessment.objects.filter(
                result__course__lecturer=user.id, result_id=self.kwargs.get("result_pk")
            ).exclude(result__status="D")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update(
            {
                "result": getattr(self, "_cached_result", None),
                "result_id": self.kwargs.get("result_pk"),
            }
        )
        return context

    def decimal_to_float(self, value):
        """Convert Decimal to float for JSON serialization"""
        if isinstance(value, Decimal):
            return float(value)
        return value

    def get_changes(self, instance, validated_data):
        """Identify changed fields and return old/new values with None handling"""
        changes = {}
        for field, new_value in validated_data.items():
            # Skip read-only fields
            if field in self.serializer_class.Meta.read_only_fields:
                continue

            old_value = getattr(instance, field)

            # Handle None values
            if old_value is None and new_value is None:
                continue

            # Handle Decimal comparison
            if isinstance(old_value, Decimal) or isinstance(new_value, Decimal):
                old_value = float(old_value) if old_value is not None else None
                new_value = float(new_value) if new_value is not None else None

            # Compare values (including None cases)
            if old_value != new_value:
                changes[field] = {"old": old_value, "new": new_value}
        return changes

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        # Get only fields that were actually passed in request
        updated_fields = set(request.data.keys())
        filtered_data = {
            k: v
            for k, v in serializer.validated_data.items()
            if k in updated_fields
            and k not in self.serializer_class.Meta.read_only_fields
        }

        # Get changes with filtered data
        changes = self.get_changes(instance, filtered_data)
        submitted_time = instance.result.submitted_at

        if changes:
            # Handle post-submission changes
            if submitted_time:
                if not request.data.get("correction_reason"):
                    return Response(
                        {
                            "detail": "Correction reason is required when modifying submitted scores"
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                self.perform_update(serializer)

                ResultModificationLog.objects.create(
                    assessment=instance,
                    modified_by=request.user,
                    old_data={
                        field: change["old"] for field, change in changes.items()
                    },
                    new_data={
                        field: change["new"] for field, change in changes.items()
                    },
                    reason=request.data["correction_reason"],
                )

                return Response(serializer.data)

            # Handle pre-submission changes
            self.perform_update(serializer)
            return Response(serializer.data)

        # No actual changes detected
        return Response(
            {
                "detail": "No changes were made",
                "hint": "Submitted values match current data or you tried to update read-only fields",
            },
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
                    instance = Assessment.objects.get(id=item["id"])
                    serializer = self.get_serializer(instance, data=item, partial=True)
                    serializer.is_valid(raise_exception=True)

                    # Track changes per score
                    changes = self.get_changes(instance, serializer.validated_data)
                    if changes:
                        serializer.save()

                        logs.append(
                            ResultModificationLog(
                                assessment=instance,
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
                except Assessment.DoesNotExist:
                    results.append({"id": item.get("id"), "status": "not_found"})
                    continue
                except KeyError:
                    results.append({"id": item.get("id"), "status": "invalid_data"})
                    continue

            # Bulk create logs
            if logs:
                ResultModificationLog.objects.bulk_create(logs)

        return Response(results, status=status.HTTP_200_OK)


class CASlotMaxViewSet(
    ListModelMixin, UpdateModelMixin, RetrieveModelMixin, GenericViewSet
):
    serializer_class = CASlotMaxSerializer

    def get_queryset(self):
        return CASlotMax.objects.all().select_related("assessment__result__course")

    # def get_serializer_context(self):
    #    return {"assessment_id": self.kwargs.get("assessment_pk")}


class ResultModificationLogViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    serializer_class = ResultModificationLogSerializer
    queryset = ResultModificationLog.objects.all().select_related(
        "modified_by", "assessment", "submitted_result_score__student"
    )

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = [
    #    'submitted_result_score__id',
    #    'modified_by__id',
    #    'submitted_result_score__student__id'
    # ]


class InitialLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {"detail": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_2fa_enabled or not user.otp_secret:
            # Setup 2FA for first-time users
            otp_secret = pyotp.random_base32()
            user.otp_secret = otp_secret
            user.is_2fa_enabled = True
            user.save()
            totp = pyotp.TOTP(otp_secret)
            uri = totp.provisioning_uri(name=user.username, issuer_name="ResultSystem")
            qr = qrcode.make(uri)
            buf = io.BytesIO()
            qr.save(buf, format="PNG")
            qr_code_b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return Response(
                {
                    "detail": "2FA setup required. Scan QR code with your authenticator app.",
                    "otp_secret": otp_secret,
                    "qr_code": f"data:image/png;base64,{qr_code_b64}",
                    "user_id": user.id,
                },
                status=status.HTTP_202_ACCEPTED,
            )
        else:
            # 2FA required
            return Response(
                {"detail": "2FA code required.", "user_id": user.id},
                status=status.HTTP_202_ACCEPTED,
            )


class TwoFAVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        user_id = request.data.get("user_id")
        otp_code = request.data.get("otp_code")
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

        totp = pyotp.TOTP(user.otp_secret)
        if not totp.verify(otp_code):
            return Response(
                {"detail": "Invalid 2FA code."}, status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        )
