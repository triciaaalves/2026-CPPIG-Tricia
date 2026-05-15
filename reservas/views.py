from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages

from copias.models import Copia
from reservas.forms import ReservaModelForm, ReservaListForm
from reservas.models import Reserva
from django.urls import reverse_lazy

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
        copia = form.cleaned_data['copia']
        copia = Copia.objects.get(id=copia.id)
        copia.status = 'R'
        copia.save()
        return super().form_valid(form)

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
        reserva_id = self.kwargs.get('pk')
        copia_id = Reserva.objects.get(id=reserva_id).copia.id
        print(copia_id)
        copia = Copia.objects.get(id=copia_id)
        print(copia.status)
        copia.status = 'D'
        copia.save()
        return super().form_valid(form)