from django import forms
from django.utils import timezone

from clientes.models import Cliente
from copias.models import Copia
from .models import Reserva

class ReservaListForm(forms.Form):
    cliente = forms.ModelChoiceField(label='Usuário', queryset=Cliente.objects.all(), required=False)

class ReservaModelForm(forms.ModelForm):

    class Meta:
        model = Reserva
        fields = '__all__'
        widgets = {
            'data_prevista_reserva': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y/%m/%dT%H:%M'
            ),
        }

        error_messages = {
            'data_prevista_reserva': {'required': 'A data prevista para a reserva da cópia é um campo obrigatório'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['copia'].queryset=Copia.objects.filter(status='D')
        self.fields['data_prevista_reserva'].input_formats=['%Y-%m-%dT%H:%M']
        if self.instance and self.instance.data_prevista_reserva:
            self.initial['data_prevista_reserva'] = timezone.localtime(
                self.instance.data_prevista_reserva
            ).strftime('%Y-%m-%dT%H:%M')