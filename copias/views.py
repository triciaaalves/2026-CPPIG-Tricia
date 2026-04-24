from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import CopiaModelForm
from .models import Copia

class CopiasView(ListView):
    model = Copia
    template_name = 'copias.html'

    def get_queryset(self):
        buscar = self.request.GET.get('buscar')
        qs = super(CopiasView, self).get_queryset()

        if buscar:
            qs = qs.filter(titulo__icontains=buscar)

        if qs.count() > 0:
            paginator = Paginator(qs, 20)
            listagem = paginator.get_page(self.request.GET.get('page'))
            return listagem
        else:
            return messages.info(self.request, 'Não existem cópias cadastradas!')


class CopiaAddView(SuccessMessageMixin, CreateView):
    model = Copia
    form_class = CopiaModelForm
    template_name = 'copia_form.html'
    success_url = reverse_lazy('copias')
    success_message = 'Cópia cadastrada com sucesso!'

class CopiaUpdateView(SuccessMessageMixin, UpdateView):
    model = Copia
    form_class = CopiaModelForm
    template_name = 'copia_form.html'
    success_url = reverse_lazy('copias')
    success_message = 'Cópia alterada com sucesso!'

class CopiaDeleteView(SuccessMessageMixin, DeleteView):
    model = Copia
    template_name = 'copia_apagar.html'
    success_url = reverse_lazy('copias')
    success_message = 'Cópia apagada com sucesso!'
