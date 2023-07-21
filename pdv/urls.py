from django.urls import path
from . import views

app_name = 'pdv'
urlpatterns = [
    path('sell/', views.sell, name='sell'),
    path('search/', views.article_search),
    path('activesearch/', views.active_search),
    path('makesale/', views.make_sale, name='makesale'),
    path('article/', views.article, name='article'),
    path('article/<int:id>/', views.article_get, name='article_existing'),
    path('articles/<str:filter>/<int:index>/', views.list_articles, name='article_list'),
    path('sales/named/<str:name>/', views.sales_report_named, name='report_named'),
    path('sales/ranged/', views.sales_report, name='report_query'),
    path('sales/ranged/<str:begin>/', views.sales_report, name='report_from'),
    path('sales/ranged/<str:begin>/<str:end>/', views.sales_report, name='report'),
    path('reports/', views.reports, name='reports'),
    path('medics/', views.medics, name='medics'),
    path('prescriptions/', views.prescriptions, name='prescriptions')
]
