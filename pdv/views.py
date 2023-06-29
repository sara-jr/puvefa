from django.urls import reverse
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from django.core import serializers
from .models import Article, SingleSale, Sale
from decimal import localcontext, Decimal
from .forms import ArticleForm


# Create your views here.
def sell(request):
    context = {'title': 'Venta de articulos'}
    return render(request, 'pdv/sell.html', context)


def active_search(request):
    barname = request.GET['barname']
    articles = Article.objects.filter(
        Q(name__contains=barname) | Q(barcode__contains=barname))[:20]
    html = ''.join(map(lambda article: f'''
        <a
        @click='addOrIncrement(articles, $el.dataset)'
        class='row'
        data-name="{article.name}"
        data-id="{article.id}"
        data-price="{article.price}">
            <i>barcode</i>   
            <span>{article.barcode}</span>
            <span>{article.name}</span>
        </a>
        ''', articles))
    return HttpResponse(html)


def article_search(request):
    barname = request.GET['barname']
    data = list(map(lambda x: model_to_dict(x), Article.objects.filter(
        Q(name__contains=barname) | Q(barcode__contains=barname)
        )))
    return JsonResponse(data, safe=False)


def make_sale(request):
    if request.method != 'POST':
        return redirect('pdv:sell')
        
    sale = Sale.objects.create(amount_payed=0)
    sale.save()
    sale_data = request.POST.dict()
    del sale_data['csrfmiddlewaretoken']
    with localcontext(prec=12):
        for id, quantity in sale_data.items():
            article = Article.objects.get(id=id)
            ssale = SingleSale.objects.create(article=article, sale=sale, quantity=quantity)
            sale.amount_payed += article.price * Decimal(ssale.quantity)
            ssale.save()
    return redirect('pdv:sell')

def article(request):
    form = ArticleForm()
    context = {'name':'Artículo', 'url':reverse('pdv:article')}
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            context['error'] = form.errors
        return render(request, 'pdv/sell.html', context)
    context['form'] = form.render()
    return render(request, 'pdv/post-form.html', context)

def article_get(request, id):
    article = Article.objects.get(id=id)
    context = {}
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
        else:
            context['error'] = form.errors
        return render(request, 'pdv/sell.html', context)

    form = ArticleForm(instance=article)
    context['form'] = form.render()
    context['id'] = id
    return render(request, 'pdv/article.html', context)

def list_articles(request):
    context = {}
    index = int(request.GET['index'])
    if index <= 0:
        index = 1
    context['articles'] = Article.objects.all()[:50*index]
    return render(request, 'pdv/list.html', context)
