from django.core.exceptions import ValidationError
from django.db import models
from stdimage import StdImageField

class Livro(models.Model):
    GENERO_CHOICES = [
        ('Aventura', 'Aventura'),
        ('Biografia', 'Biografia'),
        ('Conto', 'Conto'),
        ('Drama', 'Drama'),
        ('Fantasia', 'Fantasia'),
        ('Ficção Científica', 'Ficção Científica'),
        ('História', 'História'),
        ('Poesia', 'Poesia'),
        ('Romance', 'Romance'),
        ('Suspense', 'Suspense / Terror'),
        ('Outros', 'Outros'),
    ]
    foto = StdImageField('Foto', upload_to='livros', delete_orphans=True, null=True, blank=True)
    titulo = models.CharField('Título', max_length=70)
    genero = models.CharField('Gênero', max_length=70, choices=GENERO_CHOICES, default='Outros')
    autor = models.CharField('Autor', max_length=70)
    editora = models.CharField('Editora', max_length=70)
    destaque = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo

    def clean(self):
        super().clean()

        # Se o usuário tentou marcar este livro como destaque
        if self.destaque:
            # Conta quantos livros já estão destacados no banco de dados
            total_destacados = Livro.objects.filter(destaque=True)

            # Se estivermos editando um livro existente, desconsideramos ele mesmo da contagem
            if self.pk:
                total_destacados = total_destacados.exclude(pk=self.pk)

            # Se já existirem 5 ou mais, barra o salvamento
            if total_destacados.count() >= 5:
                raise ValidationError({
                    'destaque': 'Limite atingido! Já existem 5 livros em destaque na página inicial. '
                                'Desmarque o destaque de algum outro livro antes de ativar este.'
                })