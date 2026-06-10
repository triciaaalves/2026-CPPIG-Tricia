from apscheduler.schedulers.background import BackgroundScheduler
from .models import Reserva
from biblioteca import settings

scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
_scheduler_started = False

def verificar_reserva_expirada(reserva_id):
    reserva = Reserva.objects.get(pk=reserva_id)
    # Se o usuário já foi lá e fez a retirada, a reserva NÃO está mais expirada
    # Só cancela se data_retirada continuar vazia
    if not reserva.data_retirada:
        print(f"Reserva {reserva.id} expirou. Cancelando...")
        reserva.copias.update(status='D')
        reserva.delete()
        print(f"Reserva {reserva_id} excluída com sucesso.")

def start():
    global _scheduler_started

    if _scheduler_started:
        return

    scheduler.start()
    _scheduler_started = True
