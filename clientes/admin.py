from django.contrib import admin
from .models import Cliente

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_nascimento', 'email', 'telefone')
    search_fields = ('nome', 'telefone')