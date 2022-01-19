from django.contrib import admin
from tgbot.models import Student, ProjectManager, Project


class ProjectAdmin(admin.ModelAdmin):
    raw_id_fields = ['students']


admin.site.register(Student)
admin.site.register(ProjectManager)
admin.site.register(Project, ProjectAdmin)
