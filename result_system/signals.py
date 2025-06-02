from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Assessment, Result, Enrollment

@receiver(post_save, sender=Result)
def create_assessment_for_students_in_result(sender, **kwargs):
    instance = kwargs['instance']
    course = instance.course
    enrollments = Enrollment.objects.filter(course=course)
    assessment_create = [ Assessment(result = instance,student = enrollment.student) for enrollment in enrollments ]
    if kwargs['created']:
        Assessment.objects.bulk_create(assessment_create)