from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import LivroModelForm
from .models import Livro

class LivrosView(ListView):
    model = Livro
    template_name = 'livros.html'

    def get_queryset(self):
        buscar = self.request.GET.get('buscar')
        qs = super(LivrosView, self).get_queryset()

        if buscar:
            qs = qs.filter(titulo__icontains=buscar)

        if qs.count() > 0:
            paginator = Paginator(qs, 20)
            listagem = paginator.get_page(self.request.GET.get('page'))
            return listagem
        else:
            return messages.info(self.request, 'Não existem livros cadastrados!')


class LivroAddView(SuccessMessageMixin, CreateView):
    model = Livro
    form_class = LivroModelForm
    template_name = 'livro_form.html'
    success_url = reverse_lazy('livros')
    success_message = 'Livro cadastrado com sucesso!'

class LivroUpdateView(SuccessMessageMixin, UpdateView):
    model = Livro
    form_class = LivroModelForm
    template_name = 'livro_form.html'
    success_url = reverse_lazy('livros')
    success_message = 'Livro alterado com sucesso!'

class LivroDeleteView(SuccessMessageMixin, DeleteView):
    model = Livro
    template_name = 'livro_apagar.html'
    success_url = reverse_lazy('livros')
    success_message = 'Livro apagado com sucesso!'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, f'O livro {self.object} não pode ser excluído. ' f'Esse livro está registrado em algum empréstimo/reserva')
        return redirect(success_url)
