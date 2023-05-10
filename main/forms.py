from django.forms import ModelForm

from .models import WorkObject


class WorkobjectForm(ModelForm):
    class Meta:
        model = WorkObject
        fields = '__all__'