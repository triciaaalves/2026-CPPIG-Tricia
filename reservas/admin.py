from django.contrib import admin
from .models import Reserva, Copia

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('data_prevista_reserva', 'get_copias', 'cliente', 'data_retirada')
    search_fields = ('cliente__nome',)

    def get_copias(self, obj):
        return ', '.join([copia.isbn for copia in obj.copias.all()])

    get_copias.short_description = 'Cópias reservadas'