from django.urls import path

from copias.views import CopiaAddView, CopiaUpdateView, CopiaDeleteView, CopiasView

urlpatterns = [
    path('copias', CopiasView.as_view(), name='copias'),
    path('copia/adicionar', CopiaAddView.as_view(), name='copia_adicionar'),
    path('<int:pk>/copia/editar/', CopiaUpdateView.as_view(), name='copia_editar'),
    path('<int:pk>/copia/apagar/', CopiaDeleteView.as_view(), name='copia_apagar')
]