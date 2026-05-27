from datetime import timedelta
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView
from django.contrib import messages
from emprestimos.forms import EmprestimoModelForm, EmprestimoListForm
from emprestimos.models import Emprestimo
from reservas.models import Reserva
from django.urls import reverse_lazy
from django.db.models import Count


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
        cliente = form.cleaned_data.get('cliente')
        copias_selecionadas = form.cleaned_data.get('copias').count() # quantas cópias selecionadas no formulário

        tem_atraso = Emprestimo.objects.filter(
            cliente=cliente,
            data_devolucao__isnull=True,
            data_prevista__lt=timezone.now()
        ).exists()

        if tem_atraso:
            form.add_error('cliente', 'Operação cancelada! O usuário possui livros em atraso.')
            return self.form_invalid(form)

        limite_livros = 5

        copias_ja_emprestadas = Emprestimo.objects.filter(
            cliente=cliente,
            data_devolucao__isnull=True
        ).aggregate(total=Count('copias'))['total'] or 0

        copias_ja_reservadas = Reserva.objects.filter(
            cliente=cliente,
            data_retirada__isnull=True
        ).aggregate(total=Count('copias'))['total'] or 0

        total = copias_ja_emprestadas + copias_ja_reservadas
        total_futuro = total + copias_selecionadas

        if total_futuro > limite_livros:
            disponivel = limite_livros - total
            if disponivel <= 0:
                mensagem = f'Limite excedido! O usuário já possui {limite_livros} livros entre empréstimos ativos e outras reservas.'
            elif copias_ja_reservadas == 0 or copias_ja_emprestadas == 0:
                mensagem = f'O usuário pode retirar no máximo {limite_livros} cópias.'
            else:
                mensagem = f'O usuário já tem {total} livro(s). Ele só pode retirar mais {disponivel} cópia(s).'

            form.add_error('copias', mensagem)
            return self.form_invalid(form)

        # MUDEII
        form.instance.data_prevista = timezone.now() + timedelta(days=1)
        resposta = super().form_valid(form)
        for copia in self.object.copias.all():
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