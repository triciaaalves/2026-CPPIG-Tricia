from datetime import date
from django import forms
from django.utils import timezone
from .models import Cliente

class ClienteModelForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'data_nascimento', 'telefone', 'email']
        widgets = {
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date', 'max': date.today().strftime("%Y-%m-%d"), 'class': 'form-control'}
            ),
        }

        error_messages = {
            'nome': {'required': 'O nome do cliente é um campo obrigatório'},
            'data_nascimento': {'required': 'A data de nascimento do cliente é um campo obrigatório'},
            'telefone': {'required': 'O telefone do cliente é um campo obrigatório'},
            'email': {'required': 'O e-mail do cliente é um campo obrigatório',
                      'invalid': 'Formato inválido para o e-mail',
                      'unique': 'E-mail já cadastrado'},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_nascimento'].input_formats=['%Y-%m-%d']
        if self.instance and self.instance.data_nascimento:
            self.initial['data_nascimento'] = (
                self.instance.data_nascimento
            ).strftime('%Y-%m-%d')