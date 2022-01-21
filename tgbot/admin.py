from django.contrib import admin
from tgbot.models import Student, ProjectManager, Project, ProjectTeam


@admin.action(description='Создать команды')
def make_teams_in_project(modeladmin, request, queryset):
    for project in queryset:
        project.make_teams()


class ProjectAdmin(admin.ModelAdmin):
    actions = [make_teams_in_project]


admin.site.register(Student)
admin.site.register(ProjectManager)
admin.site.register(ProjectTeam)
admin.site.register(Project, ProjectAdmin)
