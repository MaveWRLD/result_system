from rest_framework import serializers
from .models import Department, Course, Result, Profile


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['name', 'code']
 
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['user', 'department', 'phone']
        
class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['name', 'code']

class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ['course', 'student', 'score', 'author', 'is_archived',
                   'status', 'created_at', 'updated_at']

