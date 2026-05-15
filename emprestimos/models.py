from django.db import models
from django.utils import timezone

from clientes.models import Cliente
from copias.models import Copia
from secretarios.models import Secretario

class Emprestimo(models.Model):
    data_retirada = models.DateTimeField(default=timezone.now)
    data_devolucao = models.DateField(null=True, blank=True)
    data_prevista = models.DateField(null=True, blank=True)
    cliente = models.ForeignKey(Cliente, verbose_name='Clientes', on_delete=models.PROTECT)
    secretario = models.ForeignKey(Secretario, verbose_name='Secretários', on_delete=models.PROTECT)
    copias = models.ManyToManyField(Copia, through='CopiasEmprestimo', related_name="emprestimo_copias")

    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'
        ordering = ['data_retirada']

    def __str__(self):
        return self.data_retirada

class CopiasEmprestimo(models.Model):
    emprestimo = models.ForeignKey(Emprestimo, verbose_name="Empréstimo", on_delete=models.CASCADE, related_name="copias_emprestimo_emprestimo")
    copia = models.ForeignKey(Copia, verbose_name="Cópia", on_delete=models.PROTECT, related_name='copias_emprestimo_copia')

    class Meta:
        verbose_name = 'Cópia retirada'
        verbose_name_plural = 'Cópias retiradas'

    def __str__(self):
        return f'{self.copia}'