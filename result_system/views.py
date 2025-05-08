from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from .models import Result, Department, User, Course
from .serializers import (DepartmentSerializer, ResultSerializer,
                           UserSerializer, CourseSerializer)


#Department API Endpoints
class DepartmentList(ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class DepartmentDetail(RetrieveUpdateDestroyAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


#Result API ENDPOINTS
class ResultList(ListCreateAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer


class ResultDetail(RetrieveUpdateDestroyAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer


#User API Endpoint
class UserList(ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

#Course API Endpoint
class CourseList(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    
class CourseDetail(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

# Create your views here.
