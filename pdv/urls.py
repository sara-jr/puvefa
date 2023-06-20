from django.urls import path
from . import views

app_name = 'pdv'
urlpatterns = [
    path('sell/', views.sell, name='sell'),
    path('search/', views.article_search),
    path('activesearch/', views.active_search),
    path('makesale/', views.make_sale, name='makesale')
]
