from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.serializers import UserCreateSerializer as BaseUserSerializer
from .models import Result, Course, Enrollment, Assessment, Student

User = get_user_model()

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id','name', 'code', 'credit', 'program', 'lecturer_id']

    def save(self, **kwargs):
        return super().save(**kwargs)
    

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['id', 'course_id', 'created_at','submitted_at', 'updated_at']

    def create(self, validated_data):
        course_id = self.context['course_id']
        return Result.objects.create(course_id=course_id, **validated_data)

class AssessmentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.none())
    class Meta:
        model = Assessment
        fields = ['result_id', 'student', 'ca_slot1', 'ca_slot2', 'ca_slot3', 'ca_slot4', 'exam_mark', 'is_approved']

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

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']

