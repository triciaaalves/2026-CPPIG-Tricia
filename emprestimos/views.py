from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages

from copias.models import Copia
from emprestimos.forms import EmprestimoModelForm, EmprestimoListForm # CopiasEmprestimoInLine
from emprestimos.models import Emprestimo
from django.urls import reverse_lazy

class EmprestimosView(ListView):
    model = Emprestimo
    template_name = 'emprestimos.html'

    def get_context_data(self, **kwargs):
        context = super(EmprestimosView, self).get_context_data(**kwargs)
        if self.request.GET:
            form = EmprestimoListForm(self.request.GET)
        else:
            form = EmprestimoListForm()
        context['form'] = form
        return context

    def get_queryset(self):
        qs = super(EmprestimosView, self).get_queryset()
        if self.request.GET:
            form = EmprestimoListForm(self.request.GET)
            if form.is_valid():
                cliente = form.cleaned_data.get('cliente')
                secretario = form.cleaned_data.get('secretario')
                if cliente:
                    qs = qs.filter(cliente=cliente)
                if secretario:
                    qs = qs.filter(secretario=secretario)
        if qs.count() > 0:
            paginator = Paginator(qs, 20)
            listagem = paginator.get_page(self.request.GET.get('page'))
            return listagem
        else:
            return messages.info(self.request, 'Não existem empréstimos cadastrados!')

class EmprestimoAddView(SuccessMessageMixin, CreateView):
    model = Emprestimo
    form_class = EmprestimoModelForm
    template_name = 'emprestimo_form.html'
    success_url = reverse_lazy('emprestimos')
    success_message = 'Empréstimo cadastrado com sucesso!'

    def form_valid(self, form):
        resposta = super().form_valid(form)
        ids = list(
            self.object.copias.values_list('id', flat=True)
        )
        for id in ids:
            copia = Copia.objects.get(id=id)
            copia.status = 'E'
            copia.save()
        return resposta

class EmprestimoDevolucao(View):
    template_name = 'emprestimo_devolver.html'

    def get(self, request, pk):
        emprestimo = Emprestimo.objects.get(pk=pk)
        # Se o usuário tentar colocar a URL de empréstimos já devolvidos
        if emprestimo.data_devolucao:
            messages.warning(request, 'Este empréstimo já foi devolvido anteriormente!')
            return redirect('emprestimos')
        return render(request, self.template_name, {
            'emprestimo': emprestimo
        })

    def post(self, request, pk):
        emprestimo = Emprestimo.objects.get(pk=pk)
        # Se o usuário tentar colocar a URL de empréstimos já devolvidos
        if emprestimo.data_devolucao:
            messages.warning(request, 'Este empréstimo já foi devolvido anteriormente!')
            return redirect('emprestimos')
        emprestimo.data_devolucao = timezone.now()
        emprestimo.copias.update(status='D')
        emprestimo.save()
        return redirect('emprestimos')
