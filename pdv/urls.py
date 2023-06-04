from django.urls import path
from . import views

app_name = 'pdv'
urlpatterns = [
    path('sell/', views.sell)
]
