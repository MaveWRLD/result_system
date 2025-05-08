from rest_framework import serializers
from .models import Result, Department, User, Course


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'code']


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['student', 'course', 'score', 'semester', 
                  'status', 'is_archived', 'created_by', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email','role', 'department']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_name', 'course_code', 'credit_hours',
                   'semester_offered', 'lecturer', 'department']