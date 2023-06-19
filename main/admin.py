from django.contrib import admin
from .models import (
    VacationRequest,
    Work,
    WorkObject,
    WorkType,
    TotalWorkObject,
    Message,
    Vacations,
)

admin.site.register(Work)
admin.site.register(WorkObject)
admin.site.register(WorkType)
admin.site.register(TotalWorkObject)
admin.site.register(Message)
admin.site.register(Vacations)
admin.site.register(VacationRequest)
