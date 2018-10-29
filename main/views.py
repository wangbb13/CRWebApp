from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from .kits import get_address, mem_city_result, add_city_data


def index(request):
    context = {}
    return render(request, 'index.html', context)


def auxiliary(request):
    context = {'click': True}
    if '0' not in request.GET:
        context['click'] = False
    return render(request, 'auxiliary.html', context)


def add_city(request):
    city = request.POST.get('city')
    lng = request.POST.get('lng')
    lat = request.POST.get('lat')
    value = request.POST.get('val')
    add_city_data(city, lng, lat, value)
    return JsonResponse({'res': 1})


def add_search_data(request):
    city = request.POST.get('city')
    value = request.POST.get('val')
    if city in mem_city_result:
        add_city_data(city, mem_city_result[city][0], mem_city_result[city][1], value)
    else:
        lng, lat = get_address(city)
        mem_city_result[city] = [lng, lat]
        add_city_data(city, lng, lat, value)
    return JsonResponse({'res': 1})


def search_city(request):
    context = dict()
    city = request.POST.get('city')
    if city in mem_city_result:
        lng, lat = mem_city_result[city]
    else:
        lng, lat = get_address(city)
        mem_city_result[city] = [lng, lat]
    if lng is not None or lat is not None:
        context['res'] = 1
        context['lng'] = lng
        context['lat'] = lat
    else:
        context['res'] = 0
    return JsonResponse(context)
