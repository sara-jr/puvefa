from functools import reduce
import math
import datetime
from django.urls import reverse
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect
from django.db.models import Q, F
from django.core.exceptions import ObjectDoesNotExist
from django.core import serializers
from .models import *
from decimal import localcontext, Decimal
from .forms import ArticleForm, MedicForm


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

def list_articles(request, filter, index):
    ITEMS_PER_PAGE = 10
    FILTERS = {
        'low':Q(quantity__lte=F('min_quantity')),
        'soldout':Q(quantity=0)
    }

    barname = request.GET.get('barname', '')
    articles = Article.objects.all()
    context = {'filter':filter, 'index':index}
    if filter != 'all':
        articles = articles.filter(FILTERS[filter])
    if barname != '':
        articles = articles.filter(Q(name__contains=barname)|Q(barcode=barname))
    indexes = math.ceil(articles.count() / ITEMS_PER_PAGE)
    
    if index <= 0 or index > indexes:
        index = 1
    context['articles'] = articles[(index - 1)*ITEMS_PER_PAGE:index*ITEMS_PER_PAGE]
    context['indexes'] = range(1, indexes+1)
    return render(request, 'pdv/list.html', context)


def compute_sale_stats(items_sold):
    with localcontext(prec=12):
        count = reduce(
            lambda value, ssale: value + ssale.quantity,
            items_sold, 0)
        sold = reduce(
            lambda value, ssale: value + ssale.article.price*ssale.quantity,
            items_sold, Decimal(0.0))
        purchased = reduce(
            lambda value, ssale: value + ssale.article.purchase_price*ssale.quantity,
            items_sold, Decimal(0.0))
        gain = sold - purchased
        gain_percentage = round(100 - purchased/sold*100,2)
    return {'total_count':count, 'total_sold':sold, 'total_purchased':purchased, 'gain':gain, 'gain_percentage':gain_percentage}

    
def sales_report_named(request, name):
    begin = datetime.date.today()
    end = None

    match name:
        case 'today':
            end = begin
        case 'week':
            begin -= datetime.timedelta(days=begin.weekday())
            end = begin + datetime.timedelta(days=6)
        case 'month':
            begin = begin.replace(day=1)
            end = begin
            end = begin.replace(month=begin.month + 1)
            end -= datetime.timedelta(days=1)
        case _:
            return HttpResponseBadRequest('Nombre de reporte invalido')

    return sales_report(request, begin.isoformat(), end.isoformat())


def sales_report(request, begin='', end=''):
    '''Genera una página con estadisticas de venta entre las fechas [begin, end]'''
    context = {'sale_count':0}
    date_begin = datetime.date.today()
    date_end = date_begin
    if begin == '':
        begin = request.GET['begin']
        end = request.GET['end']
    
    try:
        date_begin = datetime.date.fromisoformat(begin)
        date_end = datetime.date.fromisoformat(end)
    except AttributeError as error:
        return HttpResponseBadRequest(f'Formato de fecha invalido {error.name} {error.obj}')
    
    context['begin'] = date_begin
    context['end'] = date_end
    sales = Sale.objects.filter(date__gte=date_begin)
    if date_end != date_begin:
        sales = sales.filter(date__lte=date_end)
    items_sold = SingleSale.objects.filter(sale__in=sales)

    context['sale_count'] = sales.count()
    if context['sale_count'] == 0:
        return render(request, 'pdv/sales-report.html', context)
    
    context.update(compute_sale_stats(items_sold))
    return render(request, 'pdv/sales-report.html', context)


def reports(request):
    return render(request, 'pdv/reports.html')


def medics(request):
    if request.method == 'GET':
        return render(request, 'pdv/post-form-fields.html', {'form':MedicForm()})

    context = {}
    form = MedicForm(request.POST)
    if form.is_valid():
        form.save()
    else:
        context['error'] = form.error()
    return render(request, 'pdv/sell.html', context)


def prescriptions(request):
    context = {}
    
    if request.method == 'POST':
        prescription = PrescriptionTotal() if request.POST['type'] == 'total' else PrescriptionPartial()
        prescription.sale = Sale.objects.get(pk=request.POST['sale'])
        prescription.medic = Medic.objects.get(pk=request.POST['medic'])
        prescription.save()
        context['message'] = 'Receta creada'
        return HttpResponseRedirect(request.path_info)
        
    # Ids de las ventas registradas en recetas
    sales_in_prescriptions = PrescriptionTotal.objects.only('sale') \
        .union(PrescriptionPartial.objects.only('sale')) \
        .values('sale')
    # Ventas individuales de antibioticos
    antibiotics_sold = SingleSale.objects.filter(article__category__name='Antibiotico')
    # Ventas individuales de antibioticos sin registrar en recetas
    unregistered_sales = antibiotics_sold.exclude(sale__in=sales_in_prescriptions)

    data = {}
    for id, date, name, quantity in unregistered_sales.values_list('sale', 'sale__date', 'article__name', 'quantity'):
        if not id in data:
            data[id] = {'date':date, 'articles':[]}
        else:
            data[id]['articles'].append({'name':name, 'quantity':quantity})
        
    '''
    data = {
        id:{
            date: ...,
            articles: [
                {name:..., quantity:...}
            ]
        }
    }       
    '''
    context['controlled'] = data
    context['count'] = unregistered_sales.count()
    return render(request, 'pdv/prescriptions.html', context)


def index_slicing(index, count, perpage):
    '''
    Realiza un "slizing" a un objeto para que el resultado encaje en
    el indice dado
    '''
    lower_bound = (index - 1)*perpage
    if lower_bound > count:
        return slice(perpage - count, count)

    return slice(lower_bound, lower_bound + perpage)

def prescription_list(request):
    ITEMS_PERPAGE = 20
    context = {'index': 1}
    idx = 1
    values = [
        'id', 
        'date',
        'medic__cedula',
        'medic__ssa',
        'medic__address',
        'medic__name',
        'medic__sur_name_a',
        'medic__sur_name_b'
    ]
    data = []
    slicing = index_slicing(idx, PrescriptionPartial.objects.count() + PrescriptionTotal.objects.count(), ITEMS_PERPAGE)
    partial = PrescriptionPartial.objects.values_list(*values)[slicing]
    total = PrescriptionTotal.objects.values_list(*values)[slicing]

    partial = list(map(
        lambda t: {'id':t[0], 'number':'-'*4, 'date':t[1], 'cedula':t[2], 'ssa':t[3], 'address':t[4], 'medic':f'{t[5]} {t[6]} {t[7]}', 'total':False},
        partial
    ))
    total = list(map(
        lambda t: {'id':t[0], 'number':t[0], 'date':t[1], 'cedula':t[2], 'ssa':t[3], 'address':t[4], 'medic':f'{t[5]} {t[6]} {t[7]}', 'total':True},
        total
    ))

    partial.extend(total)
    partial.sort(key=lambda t: t['date'], reverse=True)
    context['prescriptions'] = partial
    return render(request, 'pdv/prescription-list.html', context)

def medic_search(request):
    context = {}
    query = request.GET['name']
    results = Medic.objects.filter(name__contains=query)[:20]
    context['results'] = list(map(lambda medic: {'display':str(medic), 'value':medic.id}, results))
    return render(request, 'pdv/search-result.html', context) 
