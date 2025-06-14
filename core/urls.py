from django.views.generic import TemplateView
from django.urls import path
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

urlpatterns = [
    path('', TemplateView.as_view(template_name='core/index.html'), )
]