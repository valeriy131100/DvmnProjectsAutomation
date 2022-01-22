from django.contrib import admin

from tgbot.models import Student, ProjectManager, Project, ProjectTeam
from tgbot.management.commands.bot import send_not, send_deep_link


@admin.action(description='Создать команды')
def make_teams_in_project(modeladmin, request, queryset):
    for project in queryset:
        project.make_teams()


@admin.action(description='Отправить оповещение')
def send_notifications(modeladmin, request, queryset):
    for team in queryset:
        students = team.students.all()
        for student in students:
            text = student.full_name
            telegram_id = student.telegram_id
            send_not(telegram_id)


@admin.action(description='Отправить оповещение')
def send_project_offer(modeladmin, request, queryset):
    students = Student.objects.all()
    for project in queryset:
        project_id = str(project.id)
        for student in students:
            telegram_id = student.telegram_id
            send_deep_link(telegram_id, project_id)



class ProjectAdmin(admin.ModelAdmin):
    actions = [make_teams_in_project, send_project_offer]


class ProjectTeamAdmin(admin.ModelAdmin):
    actions = [send_notifications]


admin.site.register(Student)
admin.site.register(ProjectManager)
admin.site.register(ProjectTeam, ProjectTeamAdmin)
admin.site.register(Project, ProjectAdmin)
