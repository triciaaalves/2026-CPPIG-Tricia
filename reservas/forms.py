from django import forms
from django.utils import timezone

from clientes.models import Cliente
from .models import Reserva

class ReservaListForm(forms.Form):
    cliente = forms.ModelChoiceField(label='Usuário', queryset=Cliente.objects.all(), required=False)

class ReservaModelForm(forms.ModelForm):

    class Meta:
        model = Reserva
        fields = '__all__'
        widgets = {
            'data_prevista_reserva': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%d/%m/%Y'
            ),
        }

        error_messages = {
            'data_prevista_reserva': {'required': 'A data prevista para a reserva da cópia é um campo obrigatório'},
        }