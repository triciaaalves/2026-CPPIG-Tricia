from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db import transaction
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages

from copias.models import Copia
from emprestimos.forms import EmprestimoModelForm, CopiasEmprestimoInLine, EmprestimoListForm
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

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            data['frm_inline'] = CopiasEmprestimoInLine(self.request.POST)
        else:
            data['frm_inline'] = CopiasEmprestimoInLine()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        frm_inline = context['frm_inline']
        with transaction.atomic():
            if frm_inline.is_valid():
                self.object = form.save()
                frm_inline.instance = self.object
                frm_inline.save()
                for form in frm_inline:
                    copia = Copia.objects.get(id=form.instance.copia.id)
                    copia.status = 'E'
                    copia.save()
                return super().form_valid(form)
            else:
                return self.render_to_response(self.get_context_data(form=form))

class EmprestimoUpdateView(SuccessMessageMixin, UpdateView):
    model = Emprestimo
    form_class = EmprestimoModelForm
    template_name = 'emprestimo_form.html'
    success_url = reverse_lazy('emprestimos')
    success_message = 'Empréstimo alterado com sucesso!'

    def get_queryset(self):
        return super().get_queryset().prefetch_related('copias_emprestimo_emprestimo')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        if self.request.POST:
            data['frm_inline'] = CopiasEmprestimoInLine(self.request.POST, instance=self.object)
        else:
            data['frm_inline'] = CopiasEmprestimoInLine(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        frm_inline = context['frm_inline']
        with transaction.atomic():
            if frm_inline.is_valid():
                self.object = form.save()
                frm_inline.instance = self.object
                frm_inline.save()
                return super().form_valid(form)
            else:
                return self.render_to_response(self.get_context_data(form=form))

class EmprestimoDeleteView(SuccessMessageMixin, DeleteView):
    model = Emprestimo
    template_name = 'emprestimo_apagar.html'
    success_url = reverse_lazy('emprestimos')
    success_message = 'Empréstimo apagado com sucesso!'