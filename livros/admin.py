from django.contrib import admin
from .models import Livro

@admin.register(Livro)
class LivroAdmin(admin.ModelAdmin):
    fields = ('titulo', 'genero', 'autor', 'editora', 'colecao', 'foto', 'fotografia')
    list_display = ('titulo', 'genero', 'autor', 'editora', 'colecao')
    readonly_fields = ['fotografia']
    search_fields = ('titulo',)

    def fotografia(self, obj):
        if obj.foto:
            return format_html('<img width="75px" src="{}" />', obj.foto.url)
        pass
