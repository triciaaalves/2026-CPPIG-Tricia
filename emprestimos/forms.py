from django import forms
from django.forms import inlineformset_factory

from clientes.models import Cliente
from secretarios.models import Secretario
from .models import Emprestimo, CopiasEmprestimo

class EmprestimoListForm(forms.Form):
    cliente = forms.ModelChoiceField(label='Usuário', queryset=Cliente.objects.all(), required=False)
    secretario = forms.ModelChoiceField(label='Secretário', queryset=Secretario.objects.all(), required=False)

class EmprestimoModelForm(forms.ModelForm):

    class Meta:
        model = Emprestimo
        fields = ['data_retirada', 'cliente', 'secretario']
        widgets = {
            'data_retirada': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%d/%m/%YT%H:%M'
            ),
        }

        error_messages = {
            'data_retirada': {'required': 'A data de retirada da cópia é um campo obrigatório'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_retirada'].input_formats=['%d/%m/%YT%H:%M']

CopiasEmprestimoInLine = inlineformset_factory(Emprestimo, CopiasEmprestimo, fields=('copia', 'data_devolucao'), extra=1, can_delete=True,)