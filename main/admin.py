from django.contrib import admin
from .models import Work, WorkObject, WorkType

# admin.site.register(Work)
admin.site.register(WorkObject)
admin.site.register(WorkType)
