from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Category)
admin.site.register(Article)
admin.site.register(ExpiryDate)
admin.site.register(Sale)
admin.site.register(SingleSale)
admin.site.register(Medic)
admin.site.register(PrescriptionPartial)
admin.site.register(PrescriptionTotal)
admin.site.register(MedicalConsultation)
admin.site.register(ArticleSaleReport)
admin.site.register(MedicalConsultationReport)
admin.site.register(SaleReport)
admin.site.register(ControlledArticleInOut)
