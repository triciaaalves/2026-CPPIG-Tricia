from dataclasses import fields

from django import forms
from clientes.models import Cliente
from copias.models import Copia
from secretarios.models import Secretario
from .models import Emprestimo

class EmprestimoListForm(forms.Form):
    cliente = forms.ModelChoiceField(label='Usuário', queryset=Cliente.objects.all(), required=False)
    secretario = forms.ModelChoiceField(label='Secretário', queryset=Secretario.objects.all(), required=False)

class EmprestimoModelForm(forms.ModelForm):

    class Meta:
        model = Emprestimo
        fields = ['cliente', 'secretario', 'copias']
        widgets = {
            'copias': forms.CheckboxSelectMultiple()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['copias'].queryset=Copia.objects.filter(status='D')
