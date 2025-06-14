from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserSerializer
from .models import Result, Course, Enrollment, Assessment, Student, SubmittedResult, SubmittedResultScore

User = get_user_model()


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'credit', 'program', 'lecturer_id']

    def save(self, **kwargs):
        return super().save(**kwargs)


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'course_id', 'created_at',
                  'submitted_at', 'updated_at']

    def create(self, validated_data):
        course_id = self.context['course_id']
        return Result.objects.create(course_id=course_id, **validated_data)


class AssessmentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.none())

    class Meta:
        model = Assessment
        fields = ['id', 'result_id', 'student', 'ca_slot1',
                  'ca_slot2', 'ca_slot3', 'ca_slot4', 'exam_mark']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get the result from context (passed by the view)
        result = self.context.get('result')
        if result:
            # Get students enrolled in the course linked to the result
            enrolled_students = Student.objects.filter(
                enrolled_student__course=result.course
            ).distinct()
            self.fields['student'].queryset = enrolled_students

    def create(self, validated_data):
        result_id = self.context['result_id']
        return Assessment.objects.create(result_id=result_id, **validated_data)


class SubmitResultSerializer(serializers.Serializer):
    result_id = serializers.IntegerField()

    def save(self, **kwargs):
        with transaction.atomic():
            result_id = self.validated_data['result_id']
            lecturer_id = User.objects.get(id=self.context['lecturer_id'])
            submitted_result = SubmittedResult.objects.create(
                lecturer=lecturer_id)
            assessments = Assessment.objects.filter(result_id=result_id)
            submitted_result_score = [
                SubmittedResultScore(
                    submitted_result=submitted_result,
                    student=assessment.student,
                    ca_slot1=assessment.ca_slot1,
                    ca_slot2=assessment.ca_slot2,
                    ca_slot3=assessment.ca_slot3,
                    ca_slot4=assessment.ca_slot4,
                    exam_mark=assessment.exam_mark
                ) for assessment in assessments
            ]

            SubmittedResultScore.objects.bulk_create(submitted_result_score)
            Result.objects.filter(id=result_id).delete()


class SubmittedResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmittedResult
        fields = ['id', 'submitted_at', 'result_status', 'lecturer_id']


class SubmittedResultScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmittedResultScore
        fields = ['id', 'submitted_result_id', 'student_id',
                  'ca_slot1', 'ca_slot2', 'ca_slot3', 'ca_slot4', 'exam_mark']

    def create(self, validated_data):
        result_id = self.context['submitted_result_id']
        return Assessment.objects.create(result_id=result_id, **validated_data)





class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']
