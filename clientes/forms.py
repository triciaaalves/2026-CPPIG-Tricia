from django import forms
from .models import Cliente

class ClienteModelForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome', 'data_nascimento', 'email', 'senha']

        error_messages = {
            'nome': {'required': 'O nome do cliente é um campo obrigatório'},
            'data_nascimento': {'required': 'A data de nascimento do cliente é um campo obrigatório'},
            'email': {'required': 'O e-mail do cliente é um campo obrigatório',
                      'invalid': 'Formato inválido para o e-mail',
                      'unique': 'E-mail já cadastrado'},
            'telefone': {'required': 'O telefone do cliente é um campo obrigatório'},
        }