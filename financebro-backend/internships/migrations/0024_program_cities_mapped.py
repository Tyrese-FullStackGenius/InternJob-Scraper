# Generated by Django 4.1.7 on 2023-04-15 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internships', '0023_country_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='cities_mapped',
            field=models.ManyToManyField(to='internships.city'),
        ),
    ]