from django.db import models

from clientes.models import Cliente

class Reserva(models.Model):
    data_prevista_reserva = models.DateField()
    cliente = models.ForeignKey(Cliente, verbose_name='Clientes', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return self.data_prevista_reserva