from django.contrib import admin
from .models import Emprestimo, Copia

@admin.register(Emprestimo)
class EmprestimoAdmin(admin.ModelAdmin):
    list_display = ('data_retirada', 'get_copias', 'cliente', 'secretario')
    search_fields = ('cliente__nome', 'secretario__nome',)

    def get_copias(self, obj):
        return ', '.join([copia.isbn for copia in obj.copias.all()])

    get_copias.short_description = 'Cópias emprestadas'