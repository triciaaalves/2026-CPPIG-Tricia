from django.core.exceptions import ValidationError
from django.db import models
from stdimage import StdImageField
import colecoes.models

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
    colecao = models.ForeignKey(colecoes.models.Colecao, verbose_name='Coleção', on_delete=models.SET_NULL, null=True, blank=True, related_name='livros')

    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo