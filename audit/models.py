from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings


class AuditedItem(models.Model):
    EDIT = 'E'
    ARCHIVE = 'A'
    REACTIVATE = 'RA'
    ACTION_CHOICES = [
        (EDIT, 'Edit'),
        (ARCHIVE, 'Archive'),
        (REACTIVATE, 'Reactivate'),
    ]
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    # Generic relation to any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    old_value = models.JSONField(blank=True, null=True)
    new_value = models.JSONField(blank=True, null=True)
    action_time = models.DateTimeField(auto_now_add=True)
    


# Create your models here.
