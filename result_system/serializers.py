from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserSerializer
from .models import Result, Course, Enrollment, Assessment, ResultModificationLog, Student, SubmittedResult, SubmittedResultScore

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
        result = self.context.get('result')
        if result:
            enrolled_students = Student.objects.filter(
                enrolled_student__course=result.course
            ).distinct()
            self.fields['student'].queryset = enrolled_students

    def create(self, validated_data):
        result_id = self.context['result_id']
        return Assessment.objects.create(result_id=result_id, **validated_data)


class SubmitResultSerializer(serializers.Serializer):
    result_id = serializers.IntegerField(read_only=True)

    def save(self, **kwargs):
        with transaction.atomic():
            result_id = self.context['result_id']
            if Result.objects.filter(id=result_id).exists():
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

                SubmittedResultScore.objects.bulk_create(
                    submitted_result_score)
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
        read_only_fields = ('id', 'submitted_result_id', 'student_id')

    def create(self, validated_data):
        result_id = self.context['submitted_result_id']
        return Assessment.objects.create(result_id=result_id, **validated_data)


class ResultModificationLogSerializer(serializers.ModelSerializer):
    modified_by = serializers.StringRelatedField()
    student = serializers.SerializerMethodField()
    
    class Meta:
        model = ResultModificationLog
        fields = [
            'id',
            'student',
            'modified_by',
            'old_data',
            'new_data',
            'reason',
            'modified_at'
        ]
    
    def get_student(self, obj):
        return {
            'id': obj.submitted_result_score.student.id,
            'name': obj.submitted_result_score.student.name
        }
