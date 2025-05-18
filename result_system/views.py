from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from .serializers import DepartmentSerializer, CourseSerializer, \
    ResultSerializer, ProfileSerializer, UserSerializer
from .models import Department, Course, Result, Profile
from .filters import ResultFilter

User = get_user_model()

class DepartmentViewSet(ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer

class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ResultFilter


class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer

    def get_queryset(self):
        return Course.objects.filter(lecturer_id=self.kwargs['lecturer_pk'])

    def get_serializer_context(self):
        return {'lecturer_id':self.kwargs['lecturer_pk']}

class ProfileViewSet(ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class LecturerUserViewSet(ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(role='L')

class StudentUserViewSet(ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(role='S')



#class LecturerProfileViewSet(ModelViewSet):
#    serializer_class = LecturerProfileSerializer
#
#    def get_queryset(self):
#        return Profile.objects.filter(user__role='L')
#
#class LecturerViewSet(ModelViewSet):
#    serializer_class = ResultSerializer
#    def get_queryset(self):
#        return Result.objects.filter(lecturer_id=self.kwargs['user_id'])



# Create your views here.
