from django_filters.rest_framework import FilterSet
from .models import Result

class ResultFilter(FilterSet):
    class Meta:
        model = Result
        fields = {
            'course' : ['exact'],
            'student': ['exact'],
            'author': ['exact'],
        }