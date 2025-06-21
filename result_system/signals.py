from django.db.models.signals import post_save
from django.core.mail import send_mail, BadHeaderError
from django.dispatch import receiver
from templated_mail.mail import BaseEmailMessage
from .models import Assessment, Result, Enrollment, ResultModificationLog
import logging


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Result)
def create_assessment_for_students_in_result(sender, **kwargs):
    instance = kwargs['instance']
    course = instance.course
    enrollments = Enrollment.objects.filter(course=course)
    assessment_create = [Assessment(
        result=instance, student=enrollment.student) for enrollment in enrollments]
    if kwargs['created']:
        Assessment.objects.bulk_create(assessment_create)


@receiver(post_save, sender=ResultModificationLog)
def send_lecturer_email_for_result_modification(sender, **kwargs):
    if not kwargs.get('created'):
        return  # Only send for new instances

    instance = kwargs['instance']

    try:
        # Get related objects
        submitted_result_score = instance.submitted_result_score
        submitted_result = submitted_result_score.submitted_result
        lecturer = submitted_result.lecturer
        student = submitted_result_score.student
        # course = submitted_result.course
        course = 'course'

        # Prepare changes list with formatted field names
        changes = []
        field_display_names = {
            'ca_slot1': 'CA Slot 1',
            'ca_slot2': 'CA Slot 2',
            'ca_slot3': 'CA Slot 3',
            'ca_slot4': 'CA Slot 4',
            'exam_mark': 'Exam Mark',
        }

        for field, old_value in instance.old_data.items():
            new_value = instance.new_data.get(field, '')

            # Format values
            if isinstance(old_value, float):
                old_value = f"{old_value:.2f}"
            if isinstance(new_value, float):
                new_value = f"{new_value:.2f}"

            changes.append({
                'field': field_display_names.get(field, field.replace('_', ' ').title()),
                'old_value': old_value,
                'new_value': new_value
            })

        # Prepare context for email template
        context = {
            'system_name': 'University Results System',
            'domain': 'yourdomain.edu',
            'submitted_result_score': submitted_result_score,
            'student': student,
            'course': course,
            'lecturer': lecturer,
            'modified_by': instance.modified_by,
            'modified_at': instance.modified_at,
            'reason': instance.reason,
            'changes': changes,
            'detail_url': f"http:///results/{submitted_result_score.id}/",
        }

        # Send email
        message = BaseEmailMessage(
            template_name='./result_system/emails/modification_message.html',
            context=context
        )
        message.send([lecturer.email])
    except BadHeaderError:
        logger.warning("BadHeaderError prevented email sending")
