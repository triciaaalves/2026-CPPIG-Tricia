from django.urls import path

from .views import EmprestimosView, EmprestimoAddView, EmprestimoDevolucao

urlpatterns = [
    path('emprestimos', EmprestimosView.as_view(), name='emprestimos'),
    path('emprestimo/adicionar', EmprestimoAddView.as_view(), name='emprestimo_adicionar'),
    path('<int:pk>/emprestimo/devolver/', EmprestimoDevolucao.as_view(), name='emprestimo_devolver')
]