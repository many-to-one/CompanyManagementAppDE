from django.contrib import admin
from .models import Work, WorkObject, WorkType, TotalWorkObject, Message

admin.site.register(Work)
admin.site.register(WorkObject)
admin.site.register(WorkType)
admin.site.register(TotalWorkObject)
admin.site.register(Message)
