from datetime import timedelta
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView
from django.contrib import messages
from emprestimos.forms import EmprestimoModelForm, EmprestimoListForm
from reservas.models import Reserva
from django.urls import reverse_lazy
from .emprestimo import scheduler, enviar_lembrete, enviar_atraso
from .models import Emprestimo
from copias.models import Copia
from django.shortcuts import render, redirect, get_object_or_404

class EmprestimosView(PermissionRequiredMixin, ListView):
    permission_required = 'emprestimos.view_emprestimo'
    permission_denied_message = 'Visualizar empréstimo'
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

class EmprestimoAddView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'emprestimos.add_emprestimo'
    permission_denied_message = 'Cadastrar empréstimo'
    model = Emprestimo
    form_class = EmprestimoModelForm
    template_name = 'emprestimo_form.html'
    success_url = reverse_lazy('emprestimos')
    success_message = 'Empréstimo cadastrado com sucesso!'

    def form_valid(self, form):
        cliente = form.cleaned_data.get('cliente')
        copias_selecionadas = form.cleaned_data.get('copias')
        qtd_copias_selecionadas = copias_selecionadas.count()
        emprestimo = form.save(commit=False)

        # ---------- VERIFICAÇÃO DE EMPRÉSTIMOS EM ATRASO ---------- #
        tem_atraso = Emprestimo.objects.filter(
            cliente=cliente,
            data_devolucao__isnull=True,
            data_prevista__lt=timezone.now()
        ).exists()

        if tem_atraso:
            form.add_error('cliente', 'Este usuário possui empréstimos em atraso e não pode retirar livros.')
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
                mensagem = f'O usuário pode retirar no máximo {limite_livros} cópias.'
            else:
                mensagem = f'O usuário já tem {total} livro(s). Ele só pode retirar mais {disponivel} cópia(s).'
            form.add_error('copias', mensagem)
            return self.form_invalid(form)

        # ---------- VERIFICA SE O USUÁRIO JÁ É DONO DE UMA COLEÇÃO ---------- #
        colecao_exclusiva_do_cliente = None

        for emp in emprestimos_ativos:
            for c in emp.copias.all():
                col = getattr(c.livro, 'colecao', None)
                if col and getattr(col, 'tipo', None) == 'E' and getattr(col, 'dono', None) == cliente:
                    if col.fim_exclusividade and col.fim_exclusividade >= timezone.now().date():
                        colecao_exclusiva_do_cliente = col
                        break
            if colecao_exclusiva_do_cliente: break

        # Se não achou nos empréstimos, busca nas reservas ativas
        if not colecao_exclusiva_do_cliente:
            for res in reservas_ativas:
                for c in res.copias.all():
                    col = getattr(c.livro, 'colecao', None)
                    if col and getattr(col, 'tipo', None) == 'E' and getattr(col, 'dono', None) == cliente:
                        if col.fim_exclusividade and col.fim_exclusividade >= timezone.now().date():
                            colecao_exclusiva_do_cliente = col
                            break
                if colecao_exclusiva_do_cliente: break

        # ---------- VERIFICAÇÃO DE COLEÇÃO EXCLUSIVA ---------- #
        for copia in copias_selecionadas:
            # getattr (objeto, nome do atributo, padrão)
            # Verifica se o livro possui coleção, se não possui é None para não dar erro
            colecao = getattr(copia.livro, 'colecao', None)

            if colecao and getattr(colecao, 'tipo', None) == 'E':
                fim_excl = colecao.fim_exclusividade

                # A coleção já está exclusiva para outra pessoa
                # Se a exclusividade ainda está ativa E o dono não é o cliente atual, bloqueia
                if fim_excl and fim_excl >= timezone.now().date() and colecao.dono != cliente:
                    form.add_error(
                        'copias',
                        f'A coleção "{colecao.nome}" está exclusiva até {colecao.fim_exclusividade.strftime("%d/%m/%Y")} para outro usuário: {colecao.dono}.'
                    )
                    return self.form_invalid(form)

                # O usuário já é dono de uma coleção e está tentando pegar cópias de outra coleção
                if colecao_exclusiva_do_cliente and colecao != colecao_exclusiva_do_cliente:
                    form.add_error(
                        'copias',
                        f'O usuário já é dono da coleção "{colecao_exclusiva_do_cliente.nome}". Não é permitido possuir mais de uma coleção exclusiva simultaneamente.'
                    )
                    return self.form_invalid(form)

                # Armazena a coleção da cópia na variável, para se o usuário selecionar duas cópias em coleções diferentes
                if not colecao_exclusiva_do_cliente:
                    colecao_exclusiva_do_cliente = colecao

        # Define prazo previsto padrão do empréstimo (7 dias)
        form.instance.data_prevista = timezone.now() + timedelta(days=7)
        resposta = super().form_valid(form)

        # ---------- SALVAMENTO E ATUALIZAÇÃO DOS STATUS ---------- #
        for copia in self.object.copias.all():
            copia.status = 'E'
            copia.save()

            # Gerencia o ciclo de exclusividade da Coleção
            colecao = getattr(copia.livro, 'colecao', None)
            if colecao and getattr(colecao, 'tipo', None) == 'E':
                if not colecao.fim_exclusividade or colecao.fim_exclusividade < timezone.now().date():
                    colecao.dono = cliente
                    colecao.fim_exclusividade = timezone.now().date() + timedelta(days=10)
                    colecao.save()

        # ---------- ENVIAR LEMBRETE NO DIA DA DEVOLUÇÃO ---------- #
        scheduler.add_job(
            enviar_lembrete,
            'date',
            run_date=emprestimo.data_prevista,
            args=[self.object.id]
        )

        # ---------- ENVIAR LEMBRETE DE EMPRÉSTIMO EM ATRASO ---------- #
        scheduler.add_job(
            enviar_atraso,
            'date',
            run_date=emprestimo.data_prevista + timedelta(days=1),
            args=[self.object.id]
        )

        # ---------- VERIFIÇÃO DE COLEÇÃO (SUGESTÃO DE COMBOS) ---------- #
        copias_emprestadas_ids = [c.id for c in self.object.copias.all()]
        colecoes_encontradas = []

        for copia in self.object.copias.all():
            if hasattr(copia.livro, 'colecao') and copia.livro.colecao:
                if copia.livro.colecao not in colecoes_encontradas:
                    colecoes_encontradas.append(copia.livro.colecao)

        if colecoes_encontradas:
            # Verifica se existem OUTRAS cópias no acervo que estão DISPONÍVEIS ('D') destas coleções
            outras_copias_disponiveis = Copia.objects.filter(
                livro__colecao__in=colecoes_encontradas,
                status='D'
            ).exclude(livro__id__in=copias_emprestadas_ids).exists()

            # Se houver sugestões viáveis, desvia o caminho tradicional e joga para a tela de combos
            if outras_copias_disponiveis:
                return redirect('emprestimo_sugestao', pk=self.object.pk)

        return resposta

class EmprestimoSugestaoView(View):
    template_name = 'emprestimo_sugestao.html'

    def obter_dados_contexto(self, emprestimo):
        # Identifica os IDs das cópias já levados no empréstimo original
        copias_emprestadas_ids = [c.id for c in emprestimo.copias.all()]

        # Captura as coleções envolvidas
        colecoes = [c.livro.colecao for c in emprestimo.copias.all() if hasattr(c.livro, 'colecao') and c.livro.colecao]
        colecoes = list(set(colecoes))  # Remove duplicadas

        # Filtra cópias disponíveis dos outros livros que pertencem àquela coleção
        copias_sugeridas = Copia.objects.filter(
            livro__colecao__in=colecoes,
            status='D'
        ).exclude(id__in=copias_emprestadas_ids).select_related('livro')

        # Recalcula a cota atual do cliente (lembrando que o empréstimo atual já foi salvo)
        emprestimos_ativos = Emprestimo.objects.filter(cliente=emprestimo.cliente, data_devolucao__isnull=True)
        copias_ja_emprestadas = sum(e.copias.count() for e in emprestimos_ativos)

        reservas_ativas = Reserva.objects.filter(cliente=emprestimo.cliente, data_retirada__isnull=True)
        copias_ja_reservadas = sum(r.copias.count() for r in reservas_ativas)

        vagas_restantes = 7 - (copias_ja_emprestadas + copias_ja_reservadas)

        return {
            'emprestimo': emprestimo,
            'copias_sugeridas': copias_sugeridas,
            'vagas_restantes': vagas_restantes,
            'colecoes': colecoes
        }

    def get(self, request, pk):
        num_emprestimo = get_object_or_404(Emprestimo, pk=pk)
        contexto = self.obter_dados_contexto(num_emprestimo)

        # Se por acaso não restarem vagas, encerra e vai para a listagem
        if not contexto['copias_sugeridas'].exists() or contexto['vagas_restantes'] <= 0:
            return redirect('emprestimos')
        return render(request, self.template_name, contexto)

    def post(self, request, pk):
        emprestimo = get_object_or_404(Emprestimo, pk=pk)
        copias_ids = request.POST.getlist('copias_sugeridas')

        # Carrega o contexto novamente caso precise recarregar a página com erro
        contexto = self.obter_dados_contexto(emprestimo)
        vagas_restantes = contexto['vagas_restantes']

        if copias_ids:
            # Se o usuário marcou mais caixas do que a cota restante
            if len(copias_ids) > vagas_restantes:
                messages.error(
                    request,
                    f'Operação recusada! Você selecionou {len(copias_ids)} livro(s), mas este usuário só tem limite para mais {vagas_restantes}.'
                )
                # Recarrega a página de sugestão exibindo a mensagem de erro acima
                return render(request, self.template_name, contexto)

            # Se passou na validação, processa os empréstimos normalmente
            copias_para_adicionar = Copia.objects.filter(id__in=copias_ids, status='D')

            total_adicionado = 0
            for copia in copias_para_adicionar:
                copia.status = 'E'
                copia.save()
                emprestimo.copias.add(copia)
                total_adicionado += 1

            if total_adicionado > 0:
                messages.success(
                    request,
                    f'Combo aplicado com sucesso! Mais {total_adicionado} livro(s) da coleção foram adicionados ao empréstimo.'
                )
        else:
            messages.success(request, 'Empréstimo finalizado sem itens adicionais.')

        return redirect('emprestimos')

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

class EmprestimoDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = 'emprestimos.delete_emprestimo'
    permission_denied_message = 'Excluir empréstimo'
    model = Emprestimo
    template_name = 'emprestimo_apagar.html'
    success_url = reverse_lazy('emprestimos')
    success_message = 'Empréstimo apagada com sucesso!'

    def form_valid(self, form):
        emprestimo = self.get_object()
        emprestimo.copias.update(status='D')
        return super().form_valid(form)