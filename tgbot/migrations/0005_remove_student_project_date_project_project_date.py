# Generated by Django 4.0.1 on 2022-01-21 09:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tgbot', '0004_student_project_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='project_date',
        ),
        migrations.AddField(
            model_name='project',
            name='project_date',
            field=models.CharField(blank=True, choices=[(3, 'Третья неделя месяца'), (4, 'Четвертая неделя месяца')], max_length=50, verbose_name='Дата начала проекта'),
        ),
    ]
