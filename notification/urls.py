from django.urls import path
from rest_framework_nested.routers import DefaultRouter

from .views import NotificationViewset

router = DefaultRouter()
router.register("", NotificationViewset, basename="notification")

urlpatterns = router.urls
