from django.db import models

class Colecao(models.Model):
    TIPO_CHOICES = [
        ('C', 'Comunitária'),
        ('E', 'Exclusiva'),
    ]

    nome = models.CharField('Nome', max_length=100)
    tipo = models.CharField('Tipo', max_length=1, choices=TIPO_CHOICES, default='C')
    dono = models.ForeignKey('clientes.Cliente', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Dono atual")
    fim_exclusividade = models.DateField(null=True, blank=True, verbose_name="Fim da exclusividade")

    class Meta:
        verbose_name = 'Coleção'
        verbose_name_plural = 'Coleções'
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.get_tipo_display()})"