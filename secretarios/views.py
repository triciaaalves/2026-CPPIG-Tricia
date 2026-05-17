from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from secretarios.forms import SecretarioModelForm
from secretarios.models import Secretario


class SecretariosView(ListView):
    model = Secretario
    template_name = 'secretarios.html'

    def get_queryset(self):
        buscar = self.request.GET.get('buscar')
        qs = super(SecretariosView, self).get_queryset()

        if buscar:
            qs = qs.filter(nome__icontains=buscar)

        if qs.count() > 0:
            paginator = Paginator(qs, 20)
            listagem = paginator.get_page(self.request.GET.get('page'))
            return listagem
        else:
            return messages.info(self.request, 'Não existem secretários cadastrados!')

class SecretarioAddView(SuccessMessageMixin, CreateView):
    model = Secretario
    form_class = SecretarioModelForm
    template_name = 'secretario_form.html'
    success_url = reverse_lazy('secretarios')
    success_message = 'Secretário cadastrado com sucesso!'

class SecretarioUpdateView(SuccessMessageMixin, UpdateView):
    model = Secretario
    form_class = SecretarioModelForm
    template_name = 'secretario_form.html'
    success_url = reverse_lazy('secretarios')
    success_message = 'Secretário alterado com sucesso!'

class SecretarioDeleteView(SuccessMessageMixin, DeleteView):
    model = Secretario
    template_name = 'secretario_apagar.html'
    success_url = reverse_lazy('secretarios')
    success_message = 'Secretário apagado com sucesso!'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(request, f'O secretário {self.object} não pode ser excluído. ' f'Esse secretário está registrado em algum empréstimo')
        return redirect(success_url)