from django import forms
from .models import Article

class ArticleForm(forms.ModelForm):
    template_name = 'pdv/article-form.html'
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
    
