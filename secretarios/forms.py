from django import forms
from django.utils import timezone

from .models import Secretario

class SecretarioModelForm(forms.ModelForm):
    class Meta:
        model = Secretario
        fields = ['nome', 'data_nascimento', 'email', 'senha']
        widgets = {
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }

        error_messages = {
            'nome': {'required': 'O nome do secretário é um campo obrigatório'},
            'data_nascimento': {'required': 'A data de nascimento do secretário é um campo obrigatório'},
            'telefone': {'required': 'O telefone do secretário é um campo obrigatório'},
            'email': {'required': 'O e-mail do secretário é um campo obrigatório',
                      'invalid': 'Formato inválido para o e-mail',
                      'unique': 'E-mail já cadastrado'},
            'senha': {'required': 'A senha do secretário é um campo obrigatório'}
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_nascimento'].input_formats=['%Y-%m-%d']
        if self.instance and self.instance.data_nascimento:
            self.initial['data_nascimento'] = (
                self.instance.data_nascimento
            ).strftime('%Y-%m-%d')