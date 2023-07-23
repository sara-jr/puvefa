from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(verbose_name='Nombre de categoria', max_length=256, null=False)
    description = models.TextField(verbose_name='Descripcion', null=True)


class Article(models.Model):
    name = models.CharField(verbose_name='Nombre del articulo', max_length=256, unique=True, null=False)
    description = models.TextField(verbose_name='Descripcion', null=True)
    barcode = models.CharField(verbose_name='Codigo de barras', max_length=48, unique=True)
    price = models.DecimalField(verbose_name='Precio de venta', max_digits=8, decimal_places=2, null=False)
    purchase_price = models.DecimalField(verbose_name='Precio de compra', max_digits=8, decimal_places=2, null=False)
    quantity = models.IntegerField(verbose_name='Cantidad', default=1, null=False)
    min_quantity = models.IntegerField(verbose_name='Cantidad minima', default=1, null=False)
    has_iva = models.BooleanField(verbose_name='Incluye IVA', default=False, null=False)
    category = models.ForeignKey(Category, verbose_name='Categoria', on_delete=models.RESTRICT)


class ExpiryDate(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, primary_key=True)
    date = models.DateField(null=False)


class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True, null=False)
    amount_payed = models.DecimalField(max_digits=8, decimal_places=2, null=False)


class SingleSale(models.Model):
    article = models.ForeignKey(Article, on_delete=models.RESTRICT)
    sale = models.ForeignKey(Sale, on_delete=models.RESTRICT)
    quantity = models.IntegerField(default=1, null=False)


class Medic(models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=256, null=False)
    sur_name_a = models.CharField(verbose_name='Apellido Paterno', max_length=256, null=False)
    sur_name_b = models.CharField(verbose_name='Apellido Materno', max_length=256, null=True)
    address = models.TextField(verbose_name='Direccion', null=False)
    cedula = models.IntegerField(verbose_name='Cedula Profesional', null=False, unique=True)
    ssa = models.IntegerField(verbose_name='Registro de Salubridad', null=False, unique=True)


class Prescription(models.Model):
    medic = models.ForeignKey(Medic, verbose_name='Medico', on_delete=models.RESTRICT, null=False)
    date = models.DateField(verbose_name='Fecha', auto_now_add=True, null=False)


class PrescriptionSale(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.RESTRICT)
    sale = models.ForeignKey(SingleSale, on_delete=models.RESTRICT)
