# Generated by Django 5.2.4 on 2025-07-16 17:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result_system', '0020_resultmodificationlog_assessment_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessment',
            name='grade',
            field=models.CharField(blank=True, editable=False, max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='assessment',
            name='total_score',
            field=models.DecimalField(blank=True, decimal_places=2, editable=False, max_digits=5, null=True),
        ),
    ]
