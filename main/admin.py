from django.contrib import admin
from .models import (
    MessageCount,
    Subcontractor,
    VacationRequest,
    Work,
    WorkObject,
    WorkType,
    Message,
    Vacations,
    IsRead,
    Task,
    Documents,
)

admin.site.register(Work)
admin.site.register(WorkObject)
admin.site.register(WorkType)
admin.site.register(Message)
admin.site.register(MessageCount)
admin.site.register(Vacations)
admin.site.register(VacationRequest)
admin.site.register(IsRead)
admin.site.register(Task)
admin.site.register(Subcontractor)
admin.site.register(Documents)
