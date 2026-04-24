from django.db import models
from stdimage import StdImageField

import livros.models

class Copia(models.Model):
    foto = StdImageField('Foto', upload_to='copias', delete_orphans=True, null=True, blank=True)
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    ano = models.CharField('Ano', max_length=4)
    livro = models.ForeignKey(livros.models.Livro, verbose_name='Livros', on_delete=models.PROTECT, related_name='livro')

    class Meta:
        verbose_name = 'Cópia'
        verbose_name_plural = 'Cópias'

    def __str__(self):
        return self.isbn