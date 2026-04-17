from django.urls import path

from .views import SecretariosView, SecretarioAddView, SecretarioDeleteView, SecretarioUpdateView

urlpatterns = [
    path('secretarios', SecretariosView.as_view(), name='secretarios'),
    path('secretario/adicionar', SecretarioAddView.as_view(), name='secretario_adicionar'),
    path('<int:pk>/secretario/editar/', SecretarioUpdateView.as_view(), name='secretario_editar'),
    path('<int:pk>/secretario/apagar/', SecretarioDeleteView.as_view(), name='secretario_apagar')
]