from django.urls import path

from colecoes.views import ColecaoAddView, ColecaoUpdateView, ColecaoDeleteView, ColecoesView

urlpatterns = [
    path('colecoes', ColecoesView.as_view(), name='colecoes'),
    path('colecao/adicionar', ColecaoAddView.as_view(), name='colecao_adicionar'),
    path('<int:pk>/colecao/editar/', ColecaoUpdateView.as_view(), name='colecao_editar'),
    path('<int:pk>/colecao/apagar/', ColecaoDeleteView.as_view(), name='colecao_apagar')
]