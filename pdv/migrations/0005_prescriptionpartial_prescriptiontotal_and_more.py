# Generated by Django 4.2.2 on 2023-07-29 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pdv', '0004_alter_prescription_sale'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrescriptionPartial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Fecha')),
                ('medic', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pdv.medic', verbose_name='Medico')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pdv.sale')),
            ],
        ),
        migrations.CreateModel(
            name='PrescriptionTotal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Fecha')),
                ('medic', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pdv.medic', verbose_name='Medico')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pdv.sale')),
            ],
        ),
        migrations.DeleteModel(
            name='Prescription',
        ),
    ]
