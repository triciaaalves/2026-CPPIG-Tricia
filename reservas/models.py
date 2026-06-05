from django.db import models
from clientes.models import Cliente
from copias.models import Copia

class Reserva(models.Model):
    data_prevista_reserva = models.DateTimeField()
    cliente = models.ForeignKey(Cliente, verbose_name='Usuários', on_delete=models.PROTECT)
    copias = models.ManyToManyField(Copia)
    data_retirada = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = (('retirada_reserva', 'Permite fazer a retirada de uma reserva'),)
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['data_prevista_reserva']

    def __str__(self):
        return f"Reserva de {self.cliente} - {self.data_prevista_reserva.strftime('%d/%m/%Y %H:%M')}"