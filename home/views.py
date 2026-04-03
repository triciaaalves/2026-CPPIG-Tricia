from django.views.generic import TemplateView


class IndexView(TemplateView):
    template_name = 'index.html'

class PainelView(TemplateView):
    template_name = 'painel.html'
