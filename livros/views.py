from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from colecoes.models import Colecao
from .forms import LivroModelForm
from .models import Livro

class LivrosView(PermissionRequiredMixin, ListView):
    permission_required = 'livros.view_livro'
    permission_denied_message = 'Visualizar livro'
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


class LivroAddView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'livros.add_livro'
    permission_denied_message = 'Cadastrar livro'
    model = Livro
    form_class = LivroModelForm
    template_name = 'livro_form.html'
    success_url = reverse_lazy('livros')
    success_message = 'Livro cadastrado com sucesso!'

    def form_valid(self, form):
        destaque = form.cleaned_data.get('destaque')
        colecao = form.cleaned_data.get('colecao')

        # Validação de destaque
        if destaque:
            total_destacados = Livro.objects.filter(destaque=True).count()

            if total_destacados >= 5:
                form.add_error(
                    'destaque',
                    'Limite atingido! Já existem 5 livros em destaque na página inicial.'
                )
                return self.form_invalid(form)

        # Validação de coleção
        if colecao:
            livros_na_colecao = Livro.objects.filter(
                colecao=colecao
            ).count()

            if livros_na_colecao >= 5:
                form.add_error(
                    'colecao',
                    f'A coleção "{colecao}" já possui o máximo de 5 livros associados.'
                )
                return self.form_invalid(form)

        return super().form_valid(form)

class LivroUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'livros.update_livro'
    permission_denied_message = 'Editar livro'
    model = Livro
    form_class = LivroModelForm
    template_name = 'livro_form.html'
    success_url = reverse_lazy('livros')
    success_message = 'Livro alterado com sucesso!'

    def form_valid(self, form):
        destaque = form.cleaned_data.get('destaque')
        colecao = form.cleaned_data.get('colecao')
        livro = self.get_object()

        # Validação de destaque
        if destaque:
            total_destacados = Livro.objects.filter(
                destaque=True
            ).exclude(pk=livro.pk).count()
            if total_destacados >= 5:
                form.add_error(
                    'destaque', 'Limite atingido! Já existem 5 livros em destaque na página inicial.'
                )
                return self.form_invalid(form)

        # Validação de coleção
        if colecao:
            livros_na_colecao = Livro.objects.filter(
                colecao=colecao
            ).exclude(pk=livro.pk).count()
            if livros_na_colecao >= 5:
                form.add_error(
                    'colecao', f'A coleção "{colecao}" já possui o máximo de 5 livros associados.'
                )
                return self.form_invalid(form)

        return super().form_valid(form)

class LivroDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = 'livros.delete_livro'
    permission_denied_message = 'Excluir livro'
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
            messages.error(request, f'O livro {self.object} não pode ser excluído. ' f'Esse livro possui cópias.')
        return redirect(success_url)
