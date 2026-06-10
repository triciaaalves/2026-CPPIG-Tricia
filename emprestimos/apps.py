from django.apps import AppConfig


class EmprestimosConfig(AppConfig):
    name = 'emprestimos'
    verbose_name = 'Controle de Empréstimos'

    def ready(self):
        from emprestimos import emprestimo
        emprestimo.start()

