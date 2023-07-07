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
    path('sales/today/', views.sales_report, name='report_today'),
    path('sales/<str:begin>/', views.sales_report, name='report_from'),
    path('sales/<str:begin>/<str:end>/', views.sales_report, name='report'),
]
