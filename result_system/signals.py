import logging

from django.contrib.auth import get_user_model
from django.core.mail import BadHeaderError, send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from templated_mail.mail import BaseEmailMessage

from notification.utils import notify

from .models import Assessment, Enrollment, Result, ResultModificationLog

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=Result, weak=False)
def create_assessment_for_students_in_result(sender, **kwargs):
    instance = kwargs["instance"]
    course = instance.course
    enrollments = Enrollment.objects.filter(course=course)
    assessment_create = [
        Assessment(result=instance, student=enrollment.student)
        for enrollment in enrollments
    ]
    if kwargs["created"]:
        Assessment.objects.bulk_create(assessment_create)


@receiver(post_save, sender=ResultModificationLog, weak=False)
def send_lecturer_email_for_result_modification(sender, **kwargs):
    if not kwargs.get("created"):
        return  # Only send for new instances

    instance = kwargs["instance"]

    try:
        # Get related objects
        assessment = instance.assessment
        result = assessment.result
        lecturer = result.course.lecturer
        student = assessment.student
        course = result.course

        # Prepare changes list with formatted field names
        changes = []
        field_display_names = {
            "ca_slot1": "CA Slot 1",
            "ca_slot2": "CA Slot 2",
            "ca_slot3": "CA Slot 3",
            "ca_slot4": "CA Slot 4",
            "exam_mark": "Exam Mark",
        }

        for field, old_value in instance.old_data.items():
            new_value = instance.new_data.get(field, "")

            # Format values
            if isinstance(old_value, float):
                old_value = f"{old_value:.2f}"
            if isinstance(new_value, float):
                new_value = f"{new_value:.2f}"

            changes.append(
                {
                    "field": field_display_names.get(
                        field, field.replace("_", " ").title()
                    ),
                    "old_value": old_value,
                    "new_value": new_value,
                }
            )

        # Prepare context for email template
        context = {
            "system_name": "University Results System",
            "domain": "yourdomain.edu",
            "assessment": assessment,
            "student": student,
            "course": course,
            "lecturer": lecturer,
            "modified_by": instance.modified_by,
            "modified_at": instance.modified_at,
            "reason": instance.reason,
            "changes": changes,
            "detail_url": f"http://results/{assessment.id}/",
        }

        # Send email
        message = BaseEmailMessage(
            template_name="./result_system/emails/modification_message.html",
            context=context,
        )
        message.send([lecturer.email])
        print("message sent")
    except BadHeaderError:
        logger.warning("BadHeaderError prevented email sending")
    except Exception as e:  # Catch all other errors
        logger.error(f"Email failed: {str(e)}", exc_info=True)


@receiver(post_save, sender=Result, weak=False)
def send_result_notification(sender, instance, created, **kwargs):
    if not created and instance.status != "A":
        department = instance.course.program.department
        faculty = instance.course.program.department.faculty
        lecturer = instance.course.lecturer
        dro = User.objects.get(is_dro=True, profile__department=department)
        fro = User.objects.get(
            is_fro=True,
            profile__department=department,
            profile__department__faculty=faculty,
        )

        if lecturer == instance.updated_by:
            status = "L_D"
        else:
            status = instance.status

        if status == "L_D":
            recipient = lecturer
        if status == "D":
            recipient = lecturer
        if status == "P_D":
            recipient = dro
        if status == "P_F":
            recipient = fro

        VERB_MAP = {
            "D": f"{instance.updated_by} returned results for {instance.course.name}",
            "L_D": f"You have submitted results for {instance.course.name}",
            "P_D": f"{instance.updated_by} submitted results for {instance.course.name} to be approved",
            "P_F": f"{instance.updated_by} submitted results for {instance.course.name} to be approved",
        }

        notify(
            recipient=recipient,
            actor=instance.updated_by,
            verb=VERB_MAP.get(status),
            target_instance=instance,
        )
