from django.db import models

import livros.models

class Copia(models.Model):
    STATUS_CHOICE = [
        ('1', 'Disponível'),
        ('2', 'Emprestado'),
        ('3', 'Reservado'),
    ]
    isbn = models.CharField('ISBN', max_length=13, unique=True)
    ano = models.CharField('Ano', max_length=4)
    status = models.CharField('Status', max_length=70, choices=STATUS_CHOICE, default='1')
    livro = models.ForeignKey(livros.models.Livro, verbose_name='Livros', on_delete=models.PROTECT, related_name='livro')

    class Meta:
        verbose_name = 'Cópia'
        verbose_name_plural = 'Cópias'

    def __str__(self):
        return self.isbn