from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
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
    
