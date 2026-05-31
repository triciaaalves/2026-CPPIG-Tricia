from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import ColecaoModelForm
from .models import Colecao

class ColecoesView(ListView):
    model = Colecao
    template_name = 'colecoes.html'

    def get_queryset(self):
        buscar = self.request.GET.get('buscar')
        qs = super(ColecoesView, self).get_queryset()

        if buscar:
            qs = qs.filter(nome__icontains=buscar)

        if qs.count() > 0:
            paginator = Paginator(qs, 20)
            listagem = paginator.get_page(self.request.GET.get('page'))
            return listagem
        else:
            return messages.info(self.request, 'Não existem coleções cadastradas!')


class ColecaoAddView(SuccessMessageMixin, CreateView):
    model = Colecao
    form_class = ColecaoModelForm
    template_name = 'colecao_form.html'
    success_url = reverse_lazy('colecoes')
    success_message = 'Coleção cadastrada com sucesso!'

class ColecaoUpdateView(SuccessMessageMixin, UpdateView):
    model = Colecao
    form_class = ColecaoModelForm
    template_name = 'colecao_form.html'
    success_url = reverse_lazy('colecoes')
    success_message = 'Coleção alterada com sucesso!'

class ColecaoDeleteView(SuccessMessageMixin, DeleteView):
    model = Colecao
    template_name = 'colecao_apagar.html'
    success_url = reverse_lazy('colecoes')
    success_message = 'Coleção apagada com sucesso!'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()

        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                request,
                f'Não é possível excluir a coleção {self.object.nome}! '
                f'Ela possui vínculos de proteção no sistema.'
            )
            return redirect(success_url)