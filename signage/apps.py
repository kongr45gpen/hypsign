from django.apps import AppConfig

def is_database_synchronized(database):
    from django.db.migrations.executor import MigrationExecutor
    from django.db import connections
    connection = connections[database]
    connection.prepare_database()
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    return not executor.migration_plan(targets)

class SignageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'signage'

    def ready(self):
        from django_q.models import Schedule
        from django.db import DEFAULT_DB_ALIAS

        if is_database_synchronized(DEFAULT_DB_ALIAS):
            Schedule.objects.update_or_create(name='keepalive', defaults={
                'func': 'signage.tasks.send_keepalive',
                'schedule_type': Schedule.MINUTES,
                'minutes': 1,
            }) 

            Schedule.objects.update_or_create(name='checkupdates', defaults={
                'func': 'signage.tasks.check_for_updates',
                'schedule_type': Schedule.MINUTES,
                'minutes': 1,
            }) 
