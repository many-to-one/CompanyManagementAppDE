from django.contrib import admin
from .models import (
    VacationRequest,
    Work,
    WorkObject,
    WorkType,
    Message,
    Vacations,
    IsRead,
    Task,
)

admin.site.register(Work)
admin.site.register(WorkObject)
admin.site.register(WorkType)
admin.site.register(Message)
admin.site.register(Vacations)
admin.site.register(VacationRequest)
admin.site.register(IsRead)
admin.site.register(Task)
