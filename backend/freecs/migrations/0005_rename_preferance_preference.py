# Generated by Django 5.0.7 on 2024-07-25 08:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('freecs', '0004_remove_preferance_course_preferance_category'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Preferance',
            new_name='Preference',
        ),
    ]