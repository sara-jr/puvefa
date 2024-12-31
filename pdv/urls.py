from django.urls import path
from . import views

app_name = 'pdv'
urlpatterns = [
    # SALES
    path('sale/<int:id>/', views.sale_details, name='SALE'),
    path('sale/', views.sell, name='CREATE_SALE'),
    path('makesale/', views.make_sale, name='MAKESALE'),
    # ARTICLES
    path('article/', views.ArticleCreateView.as_view(), name='CREATE_ARTICLE'),
    path('article/delete/<int:pk>/', views.ArticleDeleteView.as_view(), name='DELETE_ARTICLE'),
    path('article/<int:pk>/', views.ArticleUpdateView.as_view(), name='ARTICLE'),
    path('show/articles/', views.ArticleListView.as_view(), name='SHOW_ARTICLES'),
    path('search/article/', views.ArticleSearchView.as_view(), name='ARTICLE_SEARCH'),
    path('import/json/articles/', views.article_json_import, name='ARTICLE_IMPORT_PAGE'),
    path('article/jsonfile/', views.add_articles_from_json, name='ARTICLE_IMPORT_JSON_FILE'),
    # REPORTS
    path('sales/named/<str:name>/', views.sales_report_named, name='REPORT_NAMED'),
    path('sales/ranged/', views.sales_report, name='REPORT_QUERY'),
    path('sales/ranged/<str:begin>/', views.sales_report, name='REPORT_FROM'),
    path('sales/ranged/<str:begin>/<str:end>/', views.sales_report, name='REPORT'),
    path('reports/', views.reports, name='REPORTS'),
    path('reports/daily/', views.daily_report, name='DAILY_REPORT'),
    # MEDICS
    path('medic/', views.MedicCreateView.as_view(), name='CREATE_MEDIC'),
    path('medic/<int:pk>/', views.MedicUpdateView.as_view(), name='MEDIC'),
    path('search/medics/', views.MedicSearchView.as_view(), name='SEARCH_MEDIC'),
    # PRESCRIPTIONS
    path('prescriptions/', views.prescriptions, name='PRESCRIPTIONS'),
    path('prescriptions/all/', views.prescription_list, name='PRESCRIPTIONS_LIST'),
    path('recipt/<int:id>/', views.make_recipt, name='RECIPT'),
    # MEDICAL CHECKS
    path('check/', views.check, name='CHECK'),
    path('check/make/', views.make_check, name='MAKE_CHECK'),
    path('check/list/<int:index>/', views.list_medical_consultation, name='CONSULTATION_LIST'),
]
