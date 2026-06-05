from django.contrib import admin
from .models import Secretario

@admin.register(Secretario)
class SecretarioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'data_nascimento', 'email')
    search_fields = ('nome',)
