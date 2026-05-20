from django.db import models

import livros.models

class Copia(models.Model):
    STATUS_CHOICE = [
        ('D', 'Disponível'),
        ('E', 'Emprestado'),
        ('R', 'Reservado'),
    ]
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    ano = models.CharField('Ano', max_length=4)
    status = models.CharField('Status', max_length=70, choices=STATUS_CHOICE, default='D')
    livro = models.ForeignKey(livros.models.Livro, verbose_name='Livros', on_delete=models.PROTECT, related_name='livro')

    class Meta:
        verbose_name = 'Cópia'
        verbose_name_plural = 'Cópias'

    def __str__(self):
        return f"{self.livro.titulo}"