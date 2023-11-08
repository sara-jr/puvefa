from django import forms
from . import models

class ArticleForm(forms.ModelForm):
    template_name = 'pdv/article-form.html'
    class Meta:
        model = models.Article
        fields = [        
            "name",
            "description",
            "barcode",
            "price",
            "purchase_price",
            "quantity",
            "min_quantity",
            "has_iva",
            "category"
        ]

class MedicForm(forms.ModelForm):
    class Meta:
        model = models.Medic
        fields = '__all__'
