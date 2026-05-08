from django.db import models

class Pessoa(models.Model):
    nome = models.CharField('Nome', max_length=50)
    data_nascimento = models.DateField()
    email = models.EmailField('E-mail', max_length=100, unique=True)
    senha = models.CharField('Senha', max_length=50)

    class Meta:
        abstract = True

    def __str__(self):
        return self.nome

class Cliente(Pessoa):
    telefone = models.CharField('Telefone', max_length=15)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nome']

    def __str__(self):
        return super().nome