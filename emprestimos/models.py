from django.db import models
from django.utils import timezone

from clientes.models import Cliente
from copias.models import Copia
from secretarios.models import Secretario

class Emprestimo(models.Model):
    data_retirada = models.DateField(default=timezone.now)
    data_devolucao = models.DateField(null=True, blank=True)
    data_prevista = models.DateField(null=True, blank=True)
    cliente = models.ForeignKey(Cliente, verbose_name='Clientes', on_delete=models.PROTECT)
    secretario = models.ForeignKey(Secretario, verbose_name='Secretários', on_delete=models.PROTECT)
    copias = models.ManyToManyField(Copia)

    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'
        ordering = ['data_retirada']

    def __str__(self):
        return self.data_retirada