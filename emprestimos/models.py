from django.db import models

import clientes.models
import secretarios.models

class Emprestimo(models.Model):
    data_retirada = models.DateTimeField()
    cliente = models.ForeignKey(clientes.models.Cliente, verbose_name='Clientes', on_delete=models.PROTECT)
    secretario = models.ForeignKey(secretarios.models.Secretario, verbose_name='Secretários', on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Empréstimo'
        verbose_name_plural = 'Empréstimos'

    def __str__(self):
        return self.data_retirada