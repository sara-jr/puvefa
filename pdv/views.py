from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.db.models import Q
from django.core import serializers
from .models import Article


# Create your views here.
def sell(request):
    context = {'title': 'Venta de articulos'}
    return render(request, 'pdv/sell.html', context)


def article_search(request):
    barname = request.GET['barname']
    data = list(map(lambda x: model_to_dict(x), Article.objects.filter(
        Q(name__contains=barname) | Q(barcode__contains=barname)
        )))
    return JsonResponse(data, safe=False)
