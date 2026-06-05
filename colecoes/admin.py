from django.contrib import admin
from .models import Colecao

@admin.register(Colecao)
class ColecaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'tipo', 'dono', 'fim_exclusividade')
    search_fields = ('nome',)