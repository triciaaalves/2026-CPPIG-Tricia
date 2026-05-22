from django.db import models

from clientes.models import Cliente
from copias.models import Copia


class Reserva(models.Model):
    data_prevista_reserva = models.DateTimeField()
    cliente = models.ForeignKey(Cliente, verbose_name='Usuários', on_delete=models.PROTECT)
    copia = models.ForeignKey(Copia, verbose_name='Cópias', on_delete=models.PROTECT)
    data_retirada = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['-data_prevista_reserva']

    def __str__(self):
        return f"Reserva de {self.cliente} - {self.data_prevista_reserva.strftime('%d/%m/%Y %h:%m')}"