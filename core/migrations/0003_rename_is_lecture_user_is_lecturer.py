# Generated by Django 5.2.1 on 2025-06-12 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_user_is_dro_user_is_fro_user_is_lecture'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='is_lecture',
            new_name='is_lecturer',
        ),
    ]
