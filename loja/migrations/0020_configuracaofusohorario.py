from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracaoFusoHorario',
            fields=[
                ('id', models.BigAutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('fuso_horario', models.CharField(choices=[('America/Manaus', 'UTC-4 (Horário de Manaus - AMT)'), ('America/Sao_Paulo',
                 'UTC-3 (Horário de Brasília - BRT)')], default='America/Manaus', max_length=50, verbose_name='Fuso Horário')),
                ('ultima_atualizacao', models.DateTimeField(
                    auto_now=True, verbose_name='Última Atualização')),
            ],
            options={
                'verbose_name': 'Configuração de Fuso Horário',
                'verbose_name_plural': 'Configurações de Fuso Horário',
            },
        ),
    ]
