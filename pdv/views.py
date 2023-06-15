from django.shortcuts import render
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core import serializers
from .models import Article


# Create your views here.
def sell(request):
    context = {'title': 'Venta de articulos'}
    return render(request, 'pdv/sell.html', context)


def active_search(request):
    barname = request.GET['barname']
    articles = Article.objects.filter(
        Q(name__contains=barname) | Q(barcode__contains=barname))[:20]
    html = ''.join(map(lambda article: f'''
        <a class="row wave" 
        @click='addOrIncrement(articles, $el.dataset)'
        data-name="{article.name}" 
        data-id="{article.id}" 
        data-price="{article.price}">
            <i>arrow_right_alt</i><div>{article.name}</div>
        </a>
        ''', articles))
    return HttpResponse(html)


def article_search(request):
    barname = request.GET['barname']
    data = list(map(lambda x: model_to_dict(x), Article.objects.filter(
        Q(name__contains=barname) | Q(barcode__contains=barname)
        )))
    return JsonResponse(data, safe=False)
