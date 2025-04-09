from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0020_configuracaofusohorario'),
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "CREATE TABLE IF NOT EXISTS loja_configuracaofusohorario (id BIGINT AUTO_INCREMENT PRIMARY KEY, fuso_horario VARCHAR(50) NOT NULL, ultima_atualizacao DATETIME NOT NULL);",
            ],
            reverse_sql=[
                "DROP TABLE IF EXISTS loja_configuracaofusohorario;",
            ],
        ),
    ]
