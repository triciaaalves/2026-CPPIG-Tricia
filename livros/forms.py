from django import forms
from .models import Livro

class LivroModelForm(forms.ModelForm):
    class Meta:
        model = Livro
        fields = ['foto', 'titulo', 'genero', 'autor', 'editora', 'destaque']

        # Metodo de validação para o campo "destaque"
        def contar_destaque(self):
            destaque = self.cleaned_data.get('destaque')

            if destaque:
                # Conta quantos livros já estão destacadas no banco de dados
                total_destacados = Livro.objects.filter(destaque=True)

                # Se esta editando um livro, precisa desconsiderar ele mesma da contagem
                if self.instance and self.instance.pk:
                    total_destacados = total_destacados.exclude(pk=self.instance.pk)

                if total_destacados.count() >= 5:
                    raise forms.ValidationError(
                        'Limite atingido! Já existem 5 livros em destaque na página inicial. '
                        'Desmarque o destaque de algum livro antes de adicionar este.'
                    )

            return destaque

        error_messages = {
            'titulo': {'required': 'O título do livro é um campo obrigatório'},
            'genero': {'required': 'O gênero do livro é um campo obrigatório'},
            'autor': {'required': 'O autor(a) do livro é um campo obrigatório'},
            'editora': {'required': 'A editora do livro é um campo obrigatório'},
        }