from django.db import models


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=256, null=False)
    description = models.TextField(null=True)


class Article(models.Model):
    name = models.CharField(max_length=256, unique=True, null=False)
    description = models.TextField(null=True)
    barcode = models.CharField(max_length=48, unique=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    purchase_price = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    quantity = models.IntegerField(default=1, null=False)
    min_quantity = models.IntegerField(default=1, null=False)
    has_iva = models.BooleanField(default=False, null=False)
    category = models.ForeignKey(Category)


class ExpiryDate(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, primary_key=True)
    date = models.DateField(null=False)


class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True, null=False)
    amount_payed = models.DecimalField(max_digits=8, decimal_places=2, null=False)


class SingleSale(models.Model):
    article = models.ForeignKey(Article)
    sale = models.ForeignKey(Sale)
    quantity = models.IntegerField(default=1, null=False)


class Medic(models.Model):
    name = models.CharField(max_length=256, null=False)
    sur_name_a = models.CharField(max_length=256, null=False)
    sur_name_b = models.CharField(max_length=256, null=True)
    address = models.TextField(null=False)
    cedula = models.IntegerField(null=False, unique=True)
    ssa = models.IntegerField(null=False, unique=True)


class Prescription(models.Model):
    medic = models.ForeignKey(Medic)
    sale = models.ForeignKey(SingleSale)
