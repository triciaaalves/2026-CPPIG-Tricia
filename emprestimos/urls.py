from django.urls import path
from .views import EmprestimosView, EmprestimoAddView, EmprestimoDevolucao, EmprestimoSugestaoView, EmprestimoDeleteView

urlpatterns = [
    path('emprestimos', EmprestimosView.as_view(), name='emprestimos'),
    path('emprestimo/adicionar', EmprestimoAddView.as_view(), name='emprestimo_adicionar'),
    path('<int:pk>/emprestimo/devolver/', EmprestimoDevolucao.as_view(), name='emprestimo_devolver'),
    path('emprestimo/<int:pk>/sugestao/', EmprestimoSugestaoView.as_view(), name='emprestimo_sugestao'),
    path('<int:pk>/emprestimo/apagar/', EmprestimoDeleteView.as_view(), name='emprestimo_apagar'),

]