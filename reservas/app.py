from django.apps import AppConfig

class ReservasConfig(AppConfig):
    name = 'reservas'

    def ready(self):
        from reservas import reserva
        reserva.start()