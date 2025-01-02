from django.db import models
from django.shortcuts import reverse
from .validators import make_non_whitespace_validator, make_name_validator
from . import settings


# Create your models here.
class Category(models.Model):
    name = models.CharField(verbose_name='Nombre de categoria', max_length=256, null=False)
    description = models.TextField(verbose_name='Descripcion', null=True, blank=True)

    def __str__(self):
        return self.name


class Article(models.Model):
    name = models.CharField(verbose_name='Nombre del articulo', max_length=256, unique=True, null=False,
        validators=[
            make_non_whitespace_validator('El nombre del articulo no puede ser solamente espacios', 'whitespace')
        ]
    )
    description = models.TextField(verbose_name='Descripcion', null=True, blank=True)
    barcode = models.CharField(verbose_name='Codigo de barras', max_length=48, unique=True)
    price = models.DecimalField(verbose_name='Precio de venta', max_digits=8, decimal_places=2, null=False)
    purchase_price = models.DecimalField(verbose_name='Precio de compra', max_digits=8, decimal_places=2, null=False)
    quantity = models.IntegerField(verbose_name='Cantidad', default=1, null=False)
    min_quantity = models.IntegerField(verbose_name='Cantidad minima', default=1, null=False)
    has_iva = models.BooleanField(verbose_name='Incluye IVA', default=False, null=False)
    category = models.ForeignKey(Category, verbose_name='Categoria', on_delete=models.RESTRICT)

    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse('pdv:ARTICLE', kwargs={'pk':self.pk})


class ExpiryDate(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, primary_key=True)
    date = models.DateField(null=False)


class Sale(models.Model):
    date = models.DateTimeField(auto_now_add=True, null=False)
    amount_payed = models.DecimalField(max_digits=8, decimal_places=2, null=False)

    def __str__(self):
        return f'{self.id} {self.date.isoformat(timespec="minutes", sep=" ")}'


    def has_controlled_articles(self):
        articles = SingleSale.objects.filter(sale=self.pk).only('article').values_list('article', flat=True)
        return Article.objects.filter(category__name=settings.CONTROLLED_CATEGORY_NAME, id__in=articles).exists()


class SingleSale(models.Model):
    article = models.ForeignKey(Article, on_delete=models.RESTRICT)
    sale = models.ForeignKey(Sale, on_delete=models.RESTRICT)
    quantity = models.IntegerField(default=1, null=False)


    def __str__(self):
        return f'x{self.quantity} {self.article.name}'


class Medic(models.Model):
    name = models.CharField(verbose_name='Nombre', max_length=256, null=False,
        validators=[
            make_name_validator('Nombre invalido', 'invalid')        
        ]
    )
    sur_name_a = models.CharField(verbose_name='Apellido Paterno', max_length=256, null=False,
        validators=[
            make_name_validator('Nombre invalido', 'invalid')        
        ]
    )
    sur_name_b = models.CharField(verbose_name='Apellido Materno', max_length=256, null=True,
        validators=[
            make_name_validator('Nombre invalido', 'invalid')        
        ]
    )
    address = models.TextField(verbose_name='Direccion', null=False)
    cedula = models.IntegerField(verbose_name='Cedula Profesional', null=False, unique=True)
    ssa = models.IntegerField(verbose_name='Registro de Salubridad', null=False, unique=True)

    def __str__(self):
        return f'[ {self.cedula} ] {self.name} {self.sur_name_a} {self.sur_name_b}'

    
    def get_absolute_url(self):
        return reverse('pdv:MEDIC', kwargs={'pk':self.pk})


class PrescriptionPartial(models.Model):
    medic = models.ForeignKey(Medic, verbose_name='Medico', on_delete=models.RESTRICT, null=False)
    date = models.DateField(verbose_name='Fecha', auto_now_add=True, null=False)
    sale = models.ForeignKey(Sale, null=False, on_delete=models.RESTRICT)


class PrescriptionTotal(models.Model):
    medic = models.ForeignKey(Medic, verbose_name='Medico', on_delete=models.RESTRICT, null=False)
    date = models.DateField(verbose_name='Fecha', auto_now_add=True, null=False)
    sale = models.ForeignKey(Sale, null=False, on_delete=models.RESTRICT)


class MedicalConsultation(models.Model):
    price = models.DecimalField(verbose_name='Costo', max_digits=8, decimal_places=2, null=False)
    description = models.TextField(verbose_name='Descripción', blank=True, null=False)
    date = models.DateField(verbose_name='Fecha', blank=False, null=False)
    is_consultation = models.BooleanField(verbose_name='Es consulta', null=False)


class ArticleSaleReport(models.Model):
    article = models.ForeignKey(Article, on_delete=models.RESTRICT)
    date = models.DateField(verbose_name='Fecha', auto_now_add=True, null=False)
    quantity = models.IntegerField(verbose_name='Cantidad vendida', null=False)
    total_sold = models.DecimalField(verbose_name='Venta total', max_digits=8, decimal_places=2, null=False)    
    total_cost = models.DecimalField(verbose_name='Costo total', max_digits=8, decimal_places=2, null=False)    


class MedicalConsultationReport(models.Model):
    date = models.DateField(verbose_name='Fecha', auto_now_add=True, null=False)
    total = models.DecimalField(verbose_name='Venta total', max_digits=8, decimal_places=2, null=False)    


class SaleReport(models.Model):
    date = models.DateField(verbose_name='Fecha', auto_now_add=True, null=False)
    total_sold = models.DecimalField(verbose_name='Venta total', max_digits=8, decimal_places=2, null=False)    
    total_cost = models.DecimalField(verbose_name='Costo total', max_digits=8, decimal_places=2, null=False)    
    sale_count = models.IntegerField(verbose_name='Ventas realizadas', default=0, null=False)


class ControlledArticleInOut(models.Model):
    article = models.ForeignKey(Article, on_delete=models.RESTRICT)
    date = models.DateField(verbose_name='Fecha', auto_now_add=True, null=False)
    delta = models.IntegerField(verbose_name='Cambio en cantidad', null=False)
