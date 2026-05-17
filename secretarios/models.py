from clientes.models import Pessoa

class Secretario(Pessoa):

    class Meta:
        verbose_name = 'Secretário'
        verbose_name_plural = 'Secretários'
        ordering = ['nome']

    def __str__(self):
        return super().nome
