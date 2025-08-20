from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from djoser.serializers import TokenCreateSerializer, UserSerializer
from rest_framework import serializers

from .models import (
    Assessment,
    CASlotMax,
    Course,
    Result,
    ResultModificationLog,
    UserMFA,
)

User = get_user_model()


class MFATokenCreateSerializer(TokenCreateSerializer):
    mfa_code = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        # Authenticate user first
        username = attrs.get("username")
        password = attrs.get("password")

        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )

            if not user:
                raise serializers.ValidationError(
                    {"error": "Unable to log in with provided credentials."}
                )

            # Check MFA status
            try:
                mfa = UserMFA.objects.get(user=user)
                if mfa.is_mfa_enabled:
                    mfa_code = attrs.get("mfa_code")
                    if not mfa_code:
                        raise serializers.ValidationError(
                            {"mfa_required": True, "message": "MFA code required"}
                        )

                    if not (
                        mfa.verify_totp(mfa_code) or mfa.verify_backup_code(mfa_code)
                    ):
                        raise serializers.ValidationError({"error": "Invalid MFA code"})

            except UserMFA.DoesNotExist:
                # User doesn't have MFA setup yet
                raise serializers.ValidationError(
                    {
                        "mfa_setup_required": True,
                        "message": "MFA setup required before login",
                    }
                )

            # If MFA is verified or not required, proceed
            attrs["user"] = user
            return attrs

        raise serializers.ValidationError(
            {"error": 'Must include "username" and "password".'}
        )


class MFAVerifySerializer(serializers.Serializer):
    code = serializers.CharField()


class BackupCodeSerializer(serializers.Serializer):
    code = serializers.CharField()


class MFAStatusSerializer(serializers.Serializer):
    mfa_enabled = serializers.BooleanField()
    has_backup_codes = serializers.BooleanField()


class MFASetupSerializer(serializers.Serializer):
    token = serializers.CharField()


class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = tuple(UserSerializer.Meta.fields) + (
            "is_lecturer",
            "is_dro",
            "is_fro",
            "is_co",
        )


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "name", "code", "credit", "program", "lecturer_id"]

    def save(self, **kwargs):
        return super().save(**kwargs)


class ResultSerializer(serializers.ModelSerializer):
    submitted_at = serializers.DateTimeField(read_only=True)

    # status = serializers.CharField(read_only=True)
    class Meta:
        model = Result
        fields = [
            "id",
            "course_id",
            "created_at",
            "updated_at",
            "submitted_at",
            "status",
        ]

    def create(self, validated_data):
        course_id = self.context["course_id"]
        return Result.objects.create(course_id=course_id, **validated_data)


class AssessmentSerializer(serializers.ModelSerializer):
    # student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.none())

    class Meta:
        model = Assessment
        fields = [
            "id",
            "result_id",
            "student_id",
            "ca_slot1",
            "ca_slot2",
            "ca_slot3",
            "ca_slot4",
            "exam_mark",
            "total_score",
            "grade",
        ]
        read_only_fields = ("id", "submitted_result_id", "student_id")

    # def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)
    #    result = self.context.get("result")
    #    if result:
    #        # Convert prefetched students to queryset
    #        if hasattr(result, "prefetched_assessments"):
    #            student_ids = [a.student.id for a in result.prefetched_assessments]
    #            self.fields["student"].queryset = Student.objects.filter(
    #                id__in=student_ids
    #            )
    #        else:
    #            # Fallback to optimized query
    #            self.fields["student"].queryset = Student.objects.filter(
    #                enrolled_student__course=result.course
    #            ).distinct()


class CASlotMaxSerializer(serializers.ModelSerializer):
    class Meta:
        model = CASlotMax
        fields = [
            "id",
            "assessment_id",
            "ca_slot1_max",
            "ca_slot2_max",
            "ca_slot3_max",
            "ca_slot4_max",
        ]

    # def create(self, validated_data):
    #    assessment_id = self.context["assessment_id"]
    #    return CASlotMax.objects.create(assessment_id=assessment_id, **validated_data)


class ResultModificationLogSerializer(serializers.ModelSerializer):
    modified_by = serializers.StringRelatedField()
    student = serializers.SerializerMethodField()

    class Meta:
        model = ResultModificationLog
        fields = [
            "id",
            "student",
            "modified_by",
            "old_data",
            "new_data",
            "reason",
            "modified_at",
        ]

    # def get_student(self, obj):
    #    return {
    #        "id": obj.assessment.student.id,
    #        "name": obj.assessment.student.name,
    #    }
