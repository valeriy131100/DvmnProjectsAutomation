from django.contrib import admin

from tgbot.models import Student, ProjectManager, Project, ProjectTeam
from tgbot.management.commands.bot import send_not


@admin.action(description='Создать команды')
def make_teams_in_project(modeladmin, request, queryset):
    for project in queryset:
        project.make_teams()


@admin.action(description='Отпавить оповещение')
def send_notifications(modeladmin, request, queryset):
    for team in queryset:
        students = team.students.all()
        for student in students:
            text = student.full_name
            id = student.telegram_id
            send_not(id)



class ProjectAdmin(admin.ModelAdmin):
    actions = [make_teams_in_project]


class ProjectTeamAdmin(admin.ModelAdmin):
    actions = [send_notifications]


admin.site.register(Student)
admin.site.register(ProjectManager)
admin.site.register(ProjectTeam, ProjectTeamAdmin)
admin.site.register(Project, ProjectAdmin)
