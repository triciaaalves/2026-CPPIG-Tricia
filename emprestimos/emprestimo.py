from apscheduler.schedulers.background import BackgroundScheduler
from django.core.mail import send_mail
from django.template.loader import render_to_string
from .models import Emprestimo
from biblioteca import settings

scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
_scheduler_started = False

def enviar_lembrete(emprestimo_id):
    emprestimo = Emprestimo.objects.get(pk=emprestimo_id)

    if not emprestimo.data_devolucao:
        email =[]
        email.append(emprestimo.cliente.email)

        dados = {
            'cliente': emprestimo.cliente.nome,
            'data_prevista': emprestimo.data_prevista,
            'copias': emprestimo.copias,
        }

        texto_email = render_to_string('emails/texto_email.txt', dados)
        html_email = render_to_string('emails/texto_email.html', dados)
        send_mail(subject='Lembrete de Devolução - Biblioteca Digital',
                   message=texto_email,
                  from_email='tricia.alves@acad.ufsm.br',
                  recipient_list=email,
                  html_message=html_email,
                  fail_silently=False
                )
        print(f"E-mail lembrete enviado com sucesso.")


def start():
    global _scheduler_started

    if _scheduler_started:
        return

    scheduler.start()
    _scheduler_started = True
