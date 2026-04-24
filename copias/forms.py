from django import forms
from .models import Copia

class CopiaModelForm(forms.ModelForm):

    class Meta:
        model = Copia
        fields = '__all__'

        error_messages = {
            'isbn': {'required': 'O ISBN da cópia é um campo obrigatório', 'unique': 'Código ISBN já cadastrado'},
            'ano': {'required': 'O ano da cópia é um campo obrigatório'},
        }