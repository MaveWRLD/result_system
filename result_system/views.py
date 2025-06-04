from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, UpdateModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import DjangoModelPermissions
from .models import  Course, Result, Assessment, SubmittedResult, SubmittedResultScore
from .serializers import AssessmentSerializer, CourseSerializer, SubmitResultSerializer, SubmittedResultSerializer,  UserSerializer, ResultSerializer, SubmittedResultScoreSerializer
from .permissions import  IsAdminOrReadOnly


User = get_user_model()

class CourseViewSet(ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrReadOnly]


    def get_queryset(self):
        return Course.objects.filter(lecturer_id=self.request.user.id)
    
    def get_serializer_context(self):
        return {'lecturer_id': self.request.user.id}

class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    #@action(detail=True, methods=['post', 'get'])
    #def submit(self, request):
    #    result_id = self.kwargs['result_pk']
    #    serializer = SubmitResultSerializer(data=request.data, context={'lecturer_id': request.user.id})
    #    serializer.is_valid(raise_exception=True)
    #    serializer.save()
    #    return Response(serializer.data)


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
        result_id = self.kwargs.get('result_pk')
        result = Result.objects.get(pk=result_id)
        context['result'] = result  # Pass to serializer
        context['result_id'] = result_id  # Pass to serializer

        return context
    
class SubmittedResultViewSet(ModelViewSet):
    queryset = SubmittedResult.objects.all()
    permission_classes = [DjangoModelPermissions]

    def get_queryset(self):
        user = self.request.user
        dro_role = user.user_roles.filter(role__name='DRO').first()
        lecturer_roles = user.user_roles.filter(role__name='L')
        if dro_role and dro_role.department:
            return SubmittedResult.objects.filter(result_scores__student__program__department=dro_role.department)
        elif lecturer_roles:
            return SubmittedResult.objects.filter(lecturer=user.id)
        

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SubmitResultSerializer
        return SubmittedResultSerializer


    def get_serializer_context(self):
        return {'lecturer_id': self.request.user.id}

class SubmittedResultScoreViewSet(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = SubmittedResultScore.objects.all()
    serializer_class = SubmittedResultScoreSerializer
    permission_classes = [DjangoModelPermissions]

    

# Create your views here.
