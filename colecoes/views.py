from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from .forms import ColecaoModelForm
from .models import Colecao

class ColecoesView(PermissionRequiredMixin, ListView):
    permission_required = 'colecoes.view_colecao'
    permission_denied_message = 'Visualizar coleção'
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


class ColecaoAddView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'colecoes.add_colecao'
    permission_denied_message = 'Cadastrar coleção'
    model = Colecao
    form_class = ColecaoModelForm
    template_name = 'colecao_form.html'
    success_url = reverse_lazy('colecoes')
    success_message = 'Coleção cadastrada com sucesso!'

class ColecaoUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'colecoes.update_colecao'
    permission_denied_message = 'Editar coleção'
    model = Colecao
    form_class = ColecaoModelForm
    template_name = 'colecao_form.html'
    success_url = reverse_lazy('colecoes')
    success_message = 'Coleção alterada com sucesso!'

class ColecaoDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = 'colecoes.delete_colecao'
    permission_denied_message = 'Excluir coleção'
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