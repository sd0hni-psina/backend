from django.apps import AppConfig


class PrivateMessagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.private_messages'

    def ready(self):
        import apps.private_messages.signals