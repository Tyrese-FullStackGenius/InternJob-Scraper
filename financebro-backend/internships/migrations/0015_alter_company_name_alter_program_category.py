# Generated by Django 4.1.7 on 2023-03-04 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('internships', '0014_jpmorganprogramsummary_is_copied_to_main_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='name',
            field=models.CharField(choices=[('Goldman Sachs', 'Goldman Sachs'), ('Morgan Stanley', 'Morgan Stanley'), ('JP Morgan', 'Jp Morgan'), ('Evercore', 'Evercore'), ('Lazard', 'Lazard')], max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='program',
            name='category',
            field=models.CharField(choices=[('SUMMER', 'Summer'), ('OFFCYCLE', 'Off-Cycle'), ('INSIGHT', 'Insight'), ('OTHER', 'Other')], default='OTHER', max_length=255),
        ),
    ]
