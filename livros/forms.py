from django import forms
from .models import Livro

class LivroModelForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = '__all__'

        error_messages = {
            'titulo': {'required': 'O título do livro é um campo obrigatório'},
            'genero': {'required': 'O gênero do livro é um campo obrigatório'},
            'autor': {'required': 'O autor(a) do livro é um campo obrigatório'},
            'editora': {'required': 'A editora do livro é um campo obrigatório'},
        }