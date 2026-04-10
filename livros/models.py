from django.db import models

class Livro(models.Model):
    titulo = models.CharField('Título', max_length=70)
    genero = models.CharField('Gênero', max_length=70)
    autor = models.CharField('Autor', max_length=70)
    editora = models.CharField('Editora', max_length=70)
    status = models.CharField('Status', max_length=70)


    class Meta:
        verbose_name = 'Livro'
        verbose_name_plural = 'Livros'

    def __str__(self):
        return self.titulo