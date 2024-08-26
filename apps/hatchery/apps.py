from django.apps import AppConfig


class HatcheryConfig(AppConfig):
    name = 'apps.hatchery'
    
    def ready(self) -> None:
        import apps.hatchery.signals
