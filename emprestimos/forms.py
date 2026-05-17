from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone

from clientes.models import Cliente
from copias.models import Copia
from secretarios.models import Secretario
from .models import Emprestimo, CopiasEmprestimo

class EmprestimoListForm(forms.Form):
    cliente = forms.ModelChoiceField(label='Usuário', queryset=Cliente.objects.all(), required=False)
    secretario = forms.ModelChoiceField(label='Secretário', queryset=Secretario.objects.all(), required=False)

class EmprestimoModelForm(forms.ModelForm):

    class Meta:
        model = Emprestimo
        fields = ['cliente', 'secretario']

        # error_messages = {
        #     'data_retirada': {'required': 'A data de retirada da cópia é um campo obrigatório'},
        # }

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['data_retirada'].input_formats=['%Y-%m-%dT%H:%M']
    #     if self.instance and self.instance.data_retirada:
    #         self.initial['data_retirada'] = timezone.localtime(
    #             self.instance.data_retirada
    #         ).strftime('%Y-%m-%dT%H:%M')


class EmprestimoCopiaModelForm(forms.ModelForm):

    class Meta:
        model = CopiasEmprestimo
        fields = ['copia']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['copia'].queryset=Copia.objects.filter(status='D')

CopiasEmprestimoInLine = inlineformset_factory(Emprestimo, CopiasEmprestimo, form=EmprestimoCopiaModelForm, extra=1, can_delete=False,)