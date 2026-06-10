from django.apps import AppConfig


class ReservasConfig(AppConfig):
    name = 'reservas'
    verbose_name = 'Controle de Reservas'

    def ready(self):
        from reservas import reserva
        reserva.start()
