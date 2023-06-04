from django.shortcuts import render


# Create your views here.
def sell(request):
    context = {'title': 'Venta de articulos'}
    return render(request, 'pdv/sell.html', context)

