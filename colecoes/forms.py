from django import forms
from .models import Colecao

class ColecaoModelForm(forms.ModelForm):
    class Meta:
        model = Colecao
        fields = ['nome', 'tipo']

        error_messages = {
            'nome': {'required': 'O nome da coleção é um campo obrigatório'},
            'tipo': {'required': 'O tipo da coleção é um campo obrigatório'},
        }