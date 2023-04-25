# Generated by Django 4.1.7 on 2023-04-24 22:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('signage', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='display',
            name='code',
            field=models.CharField(max_length=64, unique=True),
        ),
        migrations.CreateModel(
            name='ScheduleEntry',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('display', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signage.display')),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='signage.page')),
            ],
        ),
    ]
