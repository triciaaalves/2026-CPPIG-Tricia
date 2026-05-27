from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from datetime import timedelta
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from copias.models import Copia
from reservas.forms import ReservaModelForm, ReservaListForm
from reservas.models import Reserva
from emprestimos.models import Emprestimo
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.db.models import Count

class ReservasView(ListView):
    model = Reserva
    template_name = 'reservas.html'

    def get_context_data(self, **kwargs):
        context = super(ReservasView, self).get_context_data(**kwargs)
        if self.request.GET:
            form = ReservaListForm(self.request.GET)
        else:
            form = ReservaListForm()
        context['form'] = form
        return context

    def get_queryset(self):
        # Calcula o limite tolerável (Hora atual menos 15 minutos)
        limite_atraso = timezone.now() - timedelta(minutes=15)

        # Busca reservas não retiradas que já passaram desse limite
        reservas_expiradas = Reserva.objects.filter(
            data_retirada__isnull=True,
            # __lt = less than
            # Ele tá pegando a data prevista do usuário e vendo se é menor que o limite atraso
            data_prevista_reserva__lt=limite_atraso
        )

        # Libera as cópias e deletamos as reservas expiradas
        for r in reservas_expiradas:
            r.copias.update(status='D')
            r.delete()

        qs = super(ReservasView, self).get_queryset()
        if self.request.GET:
            form = ReservaListForm(self.request.GET)
            if form.is_valid():
                cliente = form.cleaned_data.get('cliente')
                if cliente:
                    qs = qs.filter(cliente=cliente)
        if qs.count() > 0:
            paginator = Paginator(qs, 20)
            listagem = paginator.get_page(self.request.GET.get('page'))
            return listagem
        else:
            return messages.info(self.request, 'Não existem reservas cadastradas!')

class ReservaAddView(SuccessMessageMixin, CreateView):
    model = Reserva
    form_class = ReservaModelForm
    template_name = 'reserva_form.html'
    success_url = reverse_lazy('reservas')
    success_message = 'Reserva cadastrada com sucesso!'

    def form_valid(self, form):
        cliente = form.cleaned_data.get('cliente')
        copias_selecionadas = form.cleaned_data.get('copias').count()

        # Bloqueia criação de reserva se possuir livro em atraso
        tem_atraso = Emprestimo.objects.filter(
            cliente=cliente,
            data_devolucao__isnull=True,
            data_prevista__lt=timezone.now()
        ).exists()

        if tem_atraso:
            # Mostra o erro direto no campo "cliente" do formulário HTML
            form.add_error('cliente', 'Este usuário possui empréstimos em atraso e não pode reservar livros.')
            return self.form_invalid(form)

        limite_livros = 5

        copias_ja_emprestadas = Emprestimo.objects.filter(
            cliente=cliente, data_devolucao__isnull=True
        ).aggregate(total=Count('copias'))['total'] or 0

        copias_ja_reservadas = Reserva.objects.filter(
            cliente=cliente, data_retirada__isnull=True
        ).aggregate(total=Count('copias'))['total'] or 0

        total = copias_ja_emprestadas + copias_ja_reservadas
        total_futuro = total + copias_selecionadas

        if total_futuro > limite_livros:
            disponivel = limite_livros - total
            if disponivel <= 0:
                mensagem = f'Limite excedido! O usuário já possui {limite_livros} livros entre empréstimos ativos e outras reservas.'
            elif copias_ja_reservadas == 0 or copias_ja_emprestadas == 0:
                mensagem = f'O usuário pode reservar no máximo {limite_livros} cópias.'
            else:
                mensagem = f'O usuário já tem {total} livro(s). Você só pode reservar mais {disponivel} cópia(s) para ele.'

            form.add_error('copias', mensagem)
            return self.form_invalid(form)

        resposta = super().form_valid(form)
        self.object.copias.update(status='R')
        return resposta

class ReservaUpdateView(SuccessMessageMixin, UpdateView):
    model = Reserva
    form_class = ReservaModelForm
    template_name = 'reserva_form.html'
    success_url = reverse_lazy('reservas')
    success_message = 'Reserva alterada com sucesso!'

class ReservaDeleteView(SuccessMessageMixin, DeleteView):
    model = Reserva
    template_name = 'reserva_apagar.html'
    success_url = reverse_lazy('reservas')
    success_message = 'Reserva apagada com sucesso!'

    def form_valid(self, form):
        reserva = self.get_object()
        reserva.copias.update(status='D')
        return super().form_valid(form)

class ReservaRetirada(View):
    template_name = 'reserva_retirar.html'

    def get(self, request, pk):
        reserva = Reserva.objects.get(pk=pk)
        if reserva.data_retirada:
            messages.warning(request, 'Esta retirada já foi realizada anteriormente!')
            return redirect('reservas')

        tem_atraso = Emprestimo.objects.filter(
            cliente=reserva.cliente,
            data_devolucao__isnull=True,
            data_prevista__lt=timezone.now()
        ).exists()

        if tem_atraso:
            messages.error(request, f'Operação cancelada! O usuário "{reserva.cliente}" possui livros em atraso.')
            return redirect('reservas')

        return render(request, self.template_name, {
            'reserva': reserva
        })

    def post(self, request, pk):
        reserva = Reserva.objects.get(pk=pk)
        if reserva.data_retirada:
            messages.warning(request, 'Esta retirada já foi realizada anteriormente!')
            return redirect('reservas')

        tem_atraso = Emprestimo.objects.filter(
            cliente=reserva.cliente,
            data_devolucao__isnull=True,
            data_prevista__lt=timezone.now()
        ).exists()

        if tem_atraso:
            messages.error(request, 'Operação cancelada! O usuário possui livros em atraso.')
            return redirect('reservas')

        reserva.data_retirada = timezone.now()
        reserva.save()
        reserva.copias.update(status='E')

        novo_emprestimo = Emprestimo.objects.create(
            cliente=reserva.cliente,
            data_retirada=timezone.now(),
            data_prevista=timezone.now() + timedelta(days=7)
            # como faço para o secretário???
        )
        for copia in reserva.copias.all():
            novo_emprestimo.copias.add(copia)
        return redirect('reservas')
