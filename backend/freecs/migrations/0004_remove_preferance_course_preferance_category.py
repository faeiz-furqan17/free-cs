# Generated by Django 5.0.7 on 2024-07-24 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('freecs', '0003_preferance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='preferance',
            name='course',
        ),
        migrations.AddField(
            model_name='preferance',
            name='category',
            field=models.ManyToManyField(to='freecs.category'),
        ),
    ]