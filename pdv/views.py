from functools import reduce
from django.views.decorators.http import require_POST, require_GET
import math
import datetime
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseRedirect, QueryDict
from django.db.models import Q, F, Sum
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core import serializers
from .models import *
from decimal import localcontext, Decimal
from .forms import ArticleForm, MedicForm
from .reports import *
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic.edit import FormView, DeleteView, CreateView, UpdateView
from django.views.generic import TemplateView, ListView


ITEMS_PER_PAGE = 5
MAX_SEARCH_RESULTS = 8


class ArticleCreateView(SuccessMessageMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = 'pdv/generic-form.html'
    success_message = 'Articulo creado con exito'


class ArticleDeleteView(SuccessMessageMixin, DeleteView):
    model = Article
    template_name = 'pdv/confirm-prompt.html'
    success_message = 'Articulo eliminado con exito'


class ArticleUpdateView(SuccessMessageMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = 'pdv/generic-form.html'
    success_message = 'Articulo modificado con exito'


class ArticleListView(ListView):
    paginate_by = ITEMS_PER_PAGE
    model = Article
    template_name = 'pdv/article-list.html'


    def get_queryset(self):
        params = self.request.GET
        queryset = Article.objects.all()
        if 'name' in params:
            queryset = queryset.filter(name__icontains=params['name'])
        if 'low' in params:
            queryset = queryset.filter(quantity__lte=F('min_quantity'))
        if 'barname' in params:
            queryset = queryset.filter(Q(name__icontains=params['barname']) | Q(barcode=params['barname']))

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_params = QueryDict(self.request.GET.urlencode(), mutable=True)
        if 'page' in search_params:
            search_params.pop('page')
        context['search_query'] = search_params.urlencode()
        return context
    

class MedicCreateView(SuccessMessageMixin, CreateView):
    model = Medic
    form_class = MedicForm
    template_name = 'pdv/generic-form-fields-wraped.html'
    success_message = 'Medico registrado con exito'


class MedicUpdateView(SuccessMessageMixin, UpdateView):
    model = Medic
    form_class = MedicForm
    template_name = 'pdv/geric-form-fields-wraped.html'
    success_message = 'Medico modificado con exito'


def check(request):
    return render(request, 'pdv/medical-check.html')


@require_POST
def make_check(request):
    is_consultation = request.POST['check'] == 'check'
    date = request.POST['date']
    price = request.POST['price']
    description = '' if is_consultation else request.POST['description']
    new_check = MedicalConsultation.objects.create(
        description=description, price=price, date=date, is_consultation=is_consultation)
    new_check.save()
    return redirect('pdv:check')


def sell(request):
    context = {'title': 'Venta de articulos'}
    return render(request, 'pdv/sell.html', context)


@require_GET
def active_search(request):
    context = {}
    barname = request.GET['barname']
    single = False
    try:
        articles = Article.objects.get(barcode=barname, quantity__gt=0)
        single = True
    except (MultipleObjectsReturned, ObjectDoesNotExist):
        articles = Article.objects.filter(name__contains=barname, quantity__gt=0)[:MAX_SEARCH_RESULTS]
    context['single'] = single
    context['articles'] = articles
    return render(request, 'pdv/search-result-sale.html', context)


@require_POST
def make_sale(request):
    print_recipt = request.POST['print'] == '1'
    sale = Sale.objects.create(amount_payed=Decimal(request.POST['payed']))
    sale.save()
    sale_data = request.POST.dict()
    del sale_data['csrfmiddlewaretoken']
    del sale_data['print']
    del sale_data['payed']
    with localcontext(prec=12):
        for id, quantity in sale_data.items():
            article = Article.objects.get(id=id)
            ssale = SingleSale.objects.create(article=article, sale=sale, quantity=int(quantity))
            sale.amount_payed += article.price * Decimal(ssale.quantity)
            article.quantity = article.quantity - ssale.quantity
            article.save()
            ssale.save()
    if print_recipt:
        return redirect('pdv:recipt', sale.id)
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


@require_GET
def list_articles(request, filter, index):
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
    count = articles.count()
    context['articles'] = articles[index_slicing(index, count, ITEMS_PER_PAGE)]
    context['indexes'] = index_range(count, ITEMS_PER_PAGE)
    return render(request, 'pdv/list.html', context)


@require_GET
def list_medical_consultation(request, index):
    context = {}
    medical_checks = MedicalConsultation.objects.all()
    count = medical_checks.count()
    context['medical_checks'] = medical_checks[index_slicing(index, count, ITEMS_PER_PAGE)]
    context['indexes'] = index_range(count, ITEMS_PER_PAGE)
    return render(request, 'pdv/medical-check-list.html', context)


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


def daily_report(request):
    today = datetime.date.today()
    report: SaleReport = None
    consultation_report: MedicalConsultationReport = None
    try:
        report = SaleReport.objects.get(date=today)
    except ObjectDoesNotExist:
        generate_reports(today)
        report = SaleReport.objects.get(date=today)
    try:
        consultation_report = MedicalConsultationReport.objects.get(date=today)
    except ObjectDoesNotExist:
        generate_consultation_report(today)
        consultation_report = MedicalConsultationReport.objects.get(date=today)
    article_count = ArticleSaleReport.objects.filter(date=today).only('quantity').aggregate(Sum('quantity'))['quantity__sum']
    context = dict(
        begin = today,
        end = today,
        sale_count = report.sale_count,
        total_count = article_count,
        total_sold = report.total_sold,
        total_purchased = report.total_cost,
        gain = report.total_sold - report.total_cost,
        gain_percentage = round(100 - report.total_cost/report.total_sold*100,2),
        consultation_total = consultation_report.total if consultation_report is not None else 0
    )
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



def index_range(count, perpage):
    return range(1, math.ceil(count/perpage) + 1)


def index_slicing(index, count, perpage):
    '''
    Regresa un slice que divide en n partes con un tamaño maximo y regresa la i-esima parte
    Se usa para vistas que listan objetos

    index: El indice base 1 que se desea obtener
    count: La cantidad de objetos a dividir
    perpage: La cantidad maxima de objetos en la cual se va a dividir
    '''
    lower_bound = (index - 1)*perpage
    upper_bound = lower_bound + perpage
    if lower_bound > count:
        return slice(perpage - count, count)

    if upper_bound > count:
        return slice(lower_bound, count)

    return slice(lower_bound, upper_bound)


def prescription_list(request):
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
    slicing = index_slicing(idx, PrescriptionPartial.objects.count() + PrescriptionTotal.objects.count(), ITEMS_PER_PAGE)
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


def make_recipt(request, id):
    context = {}
    sale = Sale.objects.get(pk=id)
    articles = SingleSale.objects.filter(sale=id).values_list('quantity', 'article__name', 'article__price')
    total = reduce(lambda cumm, tup: tup[0]*tup[2] + cumm, articles, 0)
    context['articles'] = list(map(
        lambda tup: {\
            'quantity':tup[0],
            'description':tup[1],
            'price':tup[2],
            'sub':tup[0]*tup[2]
        },
        articles
    ))
    context.update(
        total=total,
        change=sale.amount_payed - total,
        payed=sale.amount_payed,
        date=sale.date,
        header='HEADER',
        address='Addres #1234 TEAST'
    )
    return render(request, 'pdv/recipt.html', context)


def sale_details(request, id):
    context = {'id':id}
    sale = Sale.objects.get(pk=id)
    articles = SingleSale.objects.\
        filter(sale=sale).\
        values('article__name', 'article__category__name', 'article__price', 'quantity')
    context['articles'] = articles
    context['total'] = reduce(lambda val, item: val + item['article__price']*item['quantity'], articles, 0)
    context['payed'] = sale.amount_payed
    context['date'] = sale.date
    context['change'] =  context['payed'] - context['total']
    return render(request, 'pdv/sale-details.html', context)
    
