# Generated by Django 5.1.7 on 2025-04-05 23:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0015_moeda'),
    ]

    operations = [
        migrations.CreateModel(
            name='LogAcesso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario', models.CharField(max_length=100, verbose_name='Usuário')),
                ('data_acesso', models.DateTimeField(auto_now_add=True, verbose_name='Data de Acesso')),
                ('moedas_disponiveis', models.IntegerField(verbose_name='Moedas Disponíveis')),
                ('moedas_usadas', models.IntegerField(verbose_name='Moedas Usadas')),
            ],
            options={
                'verbose_name': 'Log de Acesso',
                'verbose_name_plural': 'Logs de Acesso',
                'ordering': ['-data_acesso'],
            },
        ),
    ]
