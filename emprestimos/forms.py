from django import forms
from .models import Emprestimo

class EmprestimoModelForm(forms.ModelForm):

    class Meta:
        model = Emprestimo
        fields = '__all__'
        widgets = {
            'data_retirada': forms.DateTimeInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }

        error_messages = {
            'data_retirada': {'required': 'A data de retirada da cópia é um campo obrigatório'},
        }