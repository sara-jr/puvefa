# Generated by Django 4.2.2 on 2023-07-21 14:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('pdv', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prescription',
            name='sale',
        ),
        migrations.AddField(
            model_name='prescription',
            name='date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Fecha'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='article',
            name='barcode',
            field=models.CharField(max_length=48, unique=True, verbose_name='Codigo de barras'),
        ),
        migrations.AlterField(
            model_name='article',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pdv.category', verbose_name='Categoria'),
        ),
        migrations.AlterField(
            model_name='article',
            name='description',
            field=models.TextField(null=True, verbose_name='Descripcion'),
        ),
        migrations.AlterField(
            model_name='article',
            name='has_iva',
            field=models.BooleanField(default=False, verbose_name='Incluye IVA'),
        ),
        migrations.AlterField(
            model_name='article',
            name='min_quantity',
            field=models.IntegerField(default=1, verbose_name='Cantidad minima'),
        ),
        migrations.AlterField(
            model_name='article',
            name='name',
            field=models.CharField(max_length=256, unique=True, verbose_name='Nombre del articulo'),
        ),
        migrations.AlterField(
            model_name='article',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Precio de venta'),
        ),
        migrations.AlterField(
            model_name='article',
            name='purchase_price',
            field=models.DecimalField(decimal_places=2, max_digits=8, verbose_name='Precio de compra'),
        ),
        migrations.AlterField(
            model_name='article',
            name='quantity',
            field=models.IntegerField(default=1, verbose_name='Cantidad'),
        ),
        migrations.AlterField(
            model_name='category',
            name='description',
            field=models.TextField(null=True, verbose_name='Descripcion'),
        ),
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=256, verbose_name='Nombre de categoria'),
        ),
        migrations.AlterField(
            model_name='medic',
            name='address',
            field=models.TextField(verbose_name='Direccion'),
        ),
        migrations.AlterField(
            model_name='medic',
            name='cedula',
            field=models.IntegerField(unique=True, verbose_name='Cedula Profesional'),
        ),
        migrations.AlterField(
            model_name='medic',
            name='name',
            field=models.CharField(max_length=256, verbose_name='Nombre'),
        ),
        migrations.AlterField(
            model_name='medic',
            name='ssa',
            field=models.IntegerField(unique=True, verbose_name='Registro de Salubridad'),
        ),
        migrations.AlterField(
            model_name='medic',
            name='sur_name_a',
            field=models.CharField(max_length=256, verbose_name='Apellido Paterno'),
        ),
        migrations.AlterField(
            model_name='medic',
            name='sur_name_b',
            field=models.CharField(max_length=256, null=True, verbose_name='Apellido Materno'),
        ),
        migrations.AlterField(
            model_name='prescription',
            name='medic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pdv.medic', verbose_name='Medico'),
        ),
        migrations.CreateModel(
            name='PrescriptionArticle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pdv.prescription')),
                ('sale', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pdv.singlesale')),
            ],
        ),
    ]
