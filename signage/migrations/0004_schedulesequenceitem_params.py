# Generated by Django 4.1.7 on 2023-04-30 01:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('signage', '0003_page_cover'),
    ]

    operations = [
        migrations.AddField(
            model_name='schedulesequenceitem',
            name='params',
            field=models.JSONField(default={}),
        ),
    ]
