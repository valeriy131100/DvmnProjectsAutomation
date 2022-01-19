# Generated by Django 4.0.1 on 2022-01-19 09:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectManager',
            fields=[
                ('telegram_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='ID в telegram')),
                ('full_name', models.CharField(max_length=200, verbose_name='ФИО')),
                ('projects_time_begin', models.TimeField(verbose_name='Начало времени проектов')),
                ('projects_time_end', models.TimeField(verbose_name='Конец времени проектов')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('telegram_id', models.IntegerField(primary_key=True, serialize=False, verbose_name='ID в telegram')),
                ('full_name', models.CharField(max_length=200, verbose_name='ФИО')),
                ('skill_level', models.CharField(choices=[('beginner', 'Новичок'), ('advanced', 'Новичок+'), ('junior', 'Джун')], max_length=50, verbose_name='Уровень навыков')),
                ('from_far_east', models.BooleanField(default=False, verbose_name='С Дальнего Востока')),
                ('preferred_time_begin', models.TimeField(blank=True, null=True, verbose_name='Предпочитаемое начало времени проектов')),
                ('preferred_time_end', models.TimeField(blank=True, null=True, verbose_name='Предпочитаемый конец времени проектов')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_time', models.TimeField(verbose_name='Время собрания по проектам')),
                ('project_manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='projects', to='tgbot.projectmanager')),
                ('students', models.ManyToManyField(related_name='projects', to='tgbot.Student', verbose_name='Участники проекта')),
            ],
        ),
    ]
