from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from .serializers import AssessmentSerializer, CourseSerializer,  UserSerializer, ResultSerializer
from .models import  Course, Result, Assessment
from .permissions import IsAdminOrReadOnly
from rest_framework import permissions
from django.db import connection
#from .filters import ResultFilter

User = get_user_model()


class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    def get_queryset(self):
        return Result.objects.filter(course_id=self.kwargs['course_pk'])

    def get_serializer_context(self):
        return {'course_id': self.kwargs['course_pk']}
 
class AssessmentViewSet(ModelViewSet):
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Extract result_pk from URL (e.g., /courses/3/results/1/assessments/)
        result_pk = self.kwargs.get('result_pk')
        result = Result.objects.get(pk=result_pk)
        context['result'] = result  # Pass to serializer
        return context
    

class CourseViewSet(ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]


    def get_queryset(self):
        return Course.objects.filter(lecturer_id=self.request.user.id)
    
    def get_serializer_context(self):
        return {'lecturer_id': self.request.user.id}

# Create your views here.
