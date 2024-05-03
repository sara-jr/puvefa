from django.urls import path
from . import views

app_name = 'pdv'
urlpatterns = [
    path('sell/', views.sell, name='sell'),
    path('makesale/', views.make_sale, name='makesale'),
    # ARTICLES
    path('article/', views.ArticleCreateView.as_view(), name='CREATE_ARTICLE'),
    path('article/delete/<int:pk>/', views.ArticleDeleteView.as_view(), name='DELETE_ARTICLE'),
    path('article/<int:pk>/', views.ArticleUpdateView.as_view(), name='ARTICLE'),
    path('show/articles/', views.ArticleListView.as_view(), name='SHOW_ARTICLES'),
    path('search/article/', views.ArticleSearchView.as_view(), name='ARTICLE_SEARCH'),

    path('sales/named/<str:name>/', views.sales_report_named, name='report_named'),
    path('sales/ranged/', views.sales_report, name='report_query'),
    path('sales/ranged/<str:begin>/', views.sales_report, name='report_from'),
    path('sales/ranged/<str:begin>/<str:end>/', views.sales_report, name='report'),
    path('reports/', views.reports, name='reports'),
    # MEDICS
    path('medic/', views.MedicCreateView.as_view(), name='CREATE_MEDIC'),
    path('medic/<int:pk>/', views.MedicUpdateView.as_view(), name='MEDIC'),
    path('search/medics/', views.MedicSearchView.as_view(), name='SEARCH_MEDIC'),

    path('prescriptions/', views.prescriptions, name='prescriptions'),
    path('prescriptions/all/', views.prescription_list, name='prescriptions_list'),
    path('recipt/<int:id>/', views.make_recipt, name='recipt'),
    path('sale/<int:id>/', views.sale_details, name='sale'),
    path('check/', views.check, name='check'),
    path('check/make/', views.make_check, name='make_check'),
    path('check/list/<int:index>/', views.list_medical_consultation, name='consultation_list'),
    path('reports/daily/', views.daily_report, name='daily_report'),
]
