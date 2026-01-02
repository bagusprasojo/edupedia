from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cbt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jawabanujian',
            name='jawaban_dipilih',
            field=models.CharField(
                blank=True,
                choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
                max_length=1,
                null=True,
            ),
        ),
    ]
