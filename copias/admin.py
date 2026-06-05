from django.contrib import admin
from .models import Copia

@admin.register(Copia)
class CopiaAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'ano', 'status', 'livro')
    search_fields = ('isbn',)