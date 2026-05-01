from django import forms
from django.forms import inlineformset_factory

from .models import Emprestimo, CopiasEmprestimo

class EmprestimoModelForm(forms.ModelForm):

    class Meta:
        model = Emprestimo
        fields = ['data_retirada', 'cliente', 'secretario']
        widgets = {
            'data_retirada': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
            'data_devolucao': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'}
            ),
        }

        error_messages = {
            'data_retirada': {'required': 'A data de retirada da cópia é um campo obrigatório'},
        }

CopiasEmprestimoInLine = inlineformset_factory(Emprestimo, CopiasEmprestimo, fields=('copia', 'data_devolucao'), extra=1, can_delete=True,)