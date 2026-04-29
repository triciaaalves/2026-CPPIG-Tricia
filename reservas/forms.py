from django import forms
from .models import Reserva

class ReservaModelForm(forms.ModelForm):

    class Meta:
        model = Reserva
        fields = '__all__'
        widgets = {
            'data_prevista_reserva': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }

        error_messages = {
            'data_prevista_reserva': {'required': 'A data prevista para a reserva da cópia é um campo obrigatório'},
        }