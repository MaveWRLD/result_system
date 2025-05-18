from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Department, Course, Result, Profile

User = get_user_model()

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'code']


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user_id', 'department_id', 'phone']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_name', 'course_code', 'credit_hours', 'department']

    def create(self, validated_data):
        lecturer_id = self.context['lecturer_id']
        return Course.objects.create(lecturer_id=lecturer_id, **validated_data)

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['course_id', 'student', 'author', 'score', 'is_archived',
                   'status', 'created_at', 'updated_at']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'role']
