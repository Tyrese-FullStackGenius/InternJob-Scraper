# Generated by Django 4.1.7 on 2023-03-03 15:08

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('internships', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='userprogram',
            unique_together={('user', 'program')},
        ),
    ]
