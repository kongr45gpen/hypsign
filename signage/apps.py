from django.apps import AppConfig


class SignageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'signage'

    def ready(self):
        from django_q.models import Schedule

        Schedule.objects.update_or_create(name='keepalive', defaults={
            'func': 'signage.tasks.send_keepalive',
            'schedule_type': Schedule.MINUTES,
            'minutes': 1,
        }) 
