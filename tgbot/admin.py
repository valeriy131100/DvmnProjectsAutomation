from django.contrib import admin
from tgbot.models import Student, ProjectManager, Project, ProjectTeam


class ProjectTeamAdmin(admin.ModelAdmin):
    raw_id_fields = ['students']


admin.site.register(Student)
admin.site.register(ProjectManager)
admin.site.register(ProjectTeam, ProjectTeamAdmin)
admin.site.register(Project)
