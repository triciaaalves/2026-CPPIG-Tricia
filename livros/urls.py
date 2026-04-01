from django.urls import path

from .views import LivrosView, LivroAddView, LivroUpdateView, LivroDeleteView

urlpatterns = [
    path('livros', LivrosView.as_view(), name='livros'),
    path('livro/adicionar/', LivroAddView.as_view(), name='livro_adicionar'),
    path('<int:pk>/livro/editar/', LivroUpdateView.as_view(), name='livro_editar'),
    path('<int:pk>/livro/apagar/', LivroDeleteView.as_view(), name='livro_apagar'),
]