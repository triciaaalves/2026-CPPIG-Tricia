from datetime import timedelta
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, DeleteView
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views import View
from copias.models import Copia
from reservas.forms import ReservaModelForm, ReservaListForm
from reservas.models import Reserva
from emprestimos.models import Emprestimo
from django.urls import reverse_lazy

from secretarios.models import Secretario
from .reserva import scheduler, verificar_reserva_expirada


class ReservasView(PermissionRequiredMixin, ListView):
    permission_required = 'reservas.view_reserva'
    permission_denied_message = 'Visualizar reserva'
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


class ReservaAddView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'reservas.add_reserva'
    permission_denied_message = 'Cadastrar reserva'
    model = Reserva
    form_class = ReservaModelForm
    template_name = 'reserva_form.html'
    success_url = reverse_lazy('reservas')
    success_message = 'Reserva cadastrada com sucesso!'

    def form_valid(self, form):
        cliente = form.cleaned_data.get('cliente')
        copias_selecionadas = form.cleaned_data.get('copias')
        qtd_copias_selecionadas = copias_selecionadas.count()
        reserva = form.save(commit=False)

        # ---------- VERIFICAÇÃO DE EMPRÉSTIMOS EM ATRASO ---------- #
        tem_atraso = Emprestimo.objects.filter(
            cliente=cliente,
            data_devolucao__isnull=True,
            data_prevista__lt=timezone.now()
        ).exists()

        if tem_atraso:
            form.add_error('cliente', 'Este usuário possui empréstimos em atraso e não pode reservar livros.')
            return self.form_invalid(form)

        # ---------- VERIFICAÇÃO DE LIMITE DE LIVROS ---------- #
        limite_livros = 7

        emprestimos_ativos = Emprestimo.objects.filter(cliente=cliente, data_devolucao__isnull=True)
        copias_ja_emprestadas = sum(e.copias.count() for e in emprestimos_ativos)

        reservas_ativas = Reserva.objects.filter(cliente=cliente, data_retirada__isnull=True)
        copias_ja_reservadas = sum(r.copias.count() for r in reservas_ativas)

        total = copias_ja_emprestadas + copias_ja_reservadas
        total_futuro = total + qtd_copias_selecionadas

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

        # ---------- VERIFICAÇÃO DE COLEÇÃO EXCLUSIVA ---------- #
        for copia in copias_selecionadas:
            colecao = getattr(copia.livro, 'colecao', None)

            if colecao and getattr(colecao, 'tipo', None) == 'E':
                fim_excl = colecao.fim_exclusividade

                if fim_excl and fim_excl >= timezone.now().date():
                    if colecao.dono != cliente:
                        form.add_error(
                            'copias',
                            f'A coleção "{colecao.nome}" está exclusiva até {colecao.fim_exclusividade.strftime("%d/%m/%Y")} para outro usuário: {colecao.dono}.'
                        )
                        return self.form_invalid(form)

        # Salva a reserva inicial se passou em tudo
        resposta = super().form_valid(form)

        # ---------- SALVAMENTO E ATUALIZAÇÃO DOS STATUS ---------- #
        for copia in self.object.copias.all():
            copia.status = 'R'  # Status: Reservado
            copia.save()

            colecao = getattr(copia.livro, 'colecao', None)
            if colecao and getattr(colecao, 'tipo', None) == 'E':
                if not colecao.fim_exclusividade or colecao.fim_exclusividade < timezone.now().date():
                    colecao.dono = cliente
                    colecao.fim_exclusividade = timezone.now().date() + timedelta(days=10)
                    colecao.save()

        # ---------- VERIFICAÇÃO DE ATRASO PARA RETIRADA (15 MIN) ---------- #
        horario_limite = self.object.data_prevista_reserva + timedelta(minutes=2)

        scheduler.add_job(
            verificar_reserva_expirada,
            'date',
            run_date=horario_limite,
            args=[self.object.id]
        )
        scheduler.get_jobs()
        reserva.save()

        # ---------- VERIFICAÇÃO DE COLEÇÃO (SUGESTÃO DE COMBOS) ---------- #
        copias_reservadas_ids = [c.id for c in self.object.copias.all()]
        colecoes_encontradas = []

        for copia in self.object.copias.all():
            if hasattr(copia.livro, 'colecao') and copia.livro.colecao:
                if copia.livro.colecao not in colecoes_encontradas:
                    colecoes_encontradas.append(copia.livro.colecao)

        if colecoes_encontradas:
            outras_copias_disponiveis = Copia.objects.filter(
                livro__colecao__in=colecoes_encontradas,
                status='D'
            ).exclude(id__in=copias_reservadas_ids).exists()

            if outras_copias_disponiveis:
                return redirect('reserva_sugestao', pk=self.object.pk)

        return resposta

class ReservaSugestaoView(View):
    template_name = 'reserva_sugestao.html'

    def obter_dados_contexto(self, reserva):
        copias_reservadas_ids = [c.id for c in reserva.copias.all()]

        colecoes = [c.livro.colecao for c in reserva.copias.all() if hasattr(c.livro, 'colecao') and c.livro.colecao]
        colecoes = list(set(colecoes))

        copias_sugeridas = Copia.objects.filter(
            livro__colecao__in=colecoes,
            status='D'
        ).exclude(id__in=copias_reservadas_ids).select_related('livro')

        emprestimos_ativos = Emprestimo.objects.filter(cliente=reserva.cliente, data_devolucao__isnull=True)
        copias_ja_emprestadas = sum(e.copias.count() for e in emprestimos_ativos)

        reservas_ativas = Reserva.objects.filter(cliente=reserva.cliente, data_retirada__isnull=True)
        copias_ja_reservadas = sum(r.copias.count() for r in reservas_ativas)

        vagas_restantes = 7 - (copias_ja_emprestadas + copias_ja_reservadas)

        return {
            'reserva': reserva,
            'copias_sugeridas': copias_sugeridas,
            'vagas_restantes': vagas_restantes,
            'colecoes': colecoes
        }

    def get(self, request, pk):
        num_reserva = get_object_or_404(Reserva, pk=pk)
        contexto = self.obter_dados_contexto(num_reserva)

        if not contexto['copias_sugeridas'].exists() or contexto['vagas_restantes'] <= 0:
            return redirect('reservas')
        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        reserva = get_object_or_404(Reserva, pk=pk)
        copias_ids = request.POST.getlist('copias_sugeridas')

        contexto = self.obter_dados_contexto(reserva)
        vagas_restantes = contexto['vagas_restantes']

        if copias_ids:
            if len(copias_ids) > vagas_restantes:
                messages.error(
                    request,
                    f'Operação recusada! Você selecionou {len(copias_ids)} livro(s), mas este usuário só tem limite para mais {vagas_restantes}.'
                )
                return render(request, self.template_name, contexto)

            copias_para_adicionar = Copia.objects.filter(id__in=copias_ids, status='D')

            total_adicionado = 0
            for copia in copias_para_adicionar:
                copia.status = 'R'
                copia.save()
                reserva.copias.add(copia)
                total_adicionado += 1

            if total_adicionado > 0:
                messages.success(
                    request,
                    f'Combo aplicado com sucesso! Mais {total_adicionado} livro(s) da coleção foram reservados.'
                )
        else:
            messages.success(request, 'Reserva finalizada sem itens adicionais.')

        return redirect('reservas')

class ReservaDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = 'reservas.delete_reserva'
    permission_denied_message = 'Excluir reserva'
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

        secretarios=Secretario.objects.all()
        return render(request, self.template_name, {
            'reserva': reserva,
            'secretarios': secretarios
        })

    def post(self, request, pk):
        reserva = Reserva.objects.get(pk=pk)
        secretario = request.POST.get('secretario')
        secretario_nome = Secretario.objects.get(pk=secretario)

        reserva.data_retirada = timezone.now()
        reserva.save()
        reserva.copias.update(status='E')

        novo_emprestimo = Emprestimo.objects.create(
            cliente=reserva.cliente,
            data_retirada=timezone.now(),
            data_prevista=timezone.now() + timedelta(days=7),
            secretario=secretario_nome
        )
        for copia in reserva.copias.all():
            novo_emprestimo.copias.add(copia)

        return redirect('reservas')