from django.shortcuts import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from .models import Result, Department, Course
from .serializers import (DepartmentSerializer, ResultSerializer,
                           CourseSerializer)


class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
   serializer_class = CourseSerializer
    


# Create your views here.
