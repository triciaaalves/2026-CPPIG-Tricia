from django.db import models
from stdimage import StdImageField

class Livro(models.Model):
    foto = StdImageField('Foto', upload_to='livros', delete_orphans=True, null=True, blank=True)
    titulo = models.CharField('Título', max_length=70)
    genero = models.CharField('Gênero', max_length=70)
    autor = models.CharField('Autor', max_length=70)
    editora = models.CharField('Editora', max_length=70)

    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'
        ordering = ['titulo']

    def __str__(self):
        return self.titulo