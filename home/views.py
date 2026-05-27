from django.views.generic import TemplateView
from livros.models import Livro

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Busca apenas as cópias com destaque ativo (garantindo o limite de 5)
        context['livros_destaque'] = Livro.objects.filter(destaque=True)[:5]

        return context

class PainelView(TemplateView):
    template_name = 'painel.html'
