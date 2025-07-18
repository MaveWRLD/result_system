from django.contrib.contenttypes.models import ContentType

from .models import Notification


def notify(recipient, actor, verb, target_instance):
    content_type = ContentType.objects.get_for_model(target_instance.__class__)
    object_id = target_instance.pk

    print("notification created")

    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        verb=verb,
        content_type=content_type,
        object_id=object_id,
    )
