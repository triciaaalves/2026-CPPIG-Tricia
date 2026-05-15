from django.db import models

from clientes.models import Cliente
from copias.models import Copia


class Reserva(models.Model):
    data_prevista_reserva = models.DateTimeField()
    cliente = models.ForeignKey(Cliente, verbose_name='Clientes', on_delete=models.PROTECT)
    copia = models.ForeignKey(Copia, verbose_name='Cópias', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['data_prevista_reserva']

    def __str__(self):
        return self.data_prevista_reserva