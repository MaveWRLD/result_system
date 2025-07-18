from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewset(ReadOnlyModelViewSet):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by(
            "-timestamp"
        )


# Create your views here.
