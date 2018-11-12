from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from .kits import get_address, mem_city_result, add_city_data, mem_yard_info, get_yard_info, get_data_from_kafka
from main.models import ReturnApplyInfo, YardInfo
from django.db.models import Sum
from datetime import datetime


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


def yard_info(request):
    if len(mem_yard_info) == 0:
        get_yard_info()
    context = {'city': [], 'loc': {}}
    temp = dict()
    start_time = request.POST.get('start')
    end_time = request.POST.get('end')
    data = ReturnApplyInfo.objects.filter(draw_datetime__gte=start_time)
    data = data.filter(draw_datetime__lte=end_time)
    data = data.values('draw_yard_code').annotate(entries=Sum('container_quantity'))
    for e in data:
        _abbr = mem_yard_info[e['draw_yard_code']]['abbr']
        _loc = mem_yard_info[e['draw_yard_code']]['loc']
        _city = mem_yard_info[e['draw_yard_code']]['city']
        if _city not in context['loc']:
            context['loc'][_city] = _loc
            temp[_city] = {
                'value': e['entries'],
                'detail': [{
                    'name': _abbr,
                    'value': e['entries']
                }]
            }
        else:
            temp[_city]['value'] += e['entries']
            temp[_city]['detail'].append({
                'name': _abbr,
                'value': e['entries']
            })
    for k, v in temp.items():
        context['city'].append({
            'name': k,
            'value': v['value'],
            'detail': v['detail']
        })
    # print(context)
    return JsonResponse(context)


ans_json = {'city': {}, 'loc': {}}


def virtual_get_stream_data():
    """
    Input: data
    Format: [
        [id, code, number, date]
    ]
    """
    global ans_json
    if len(mem_yard_info) == 0:
        get_yard_info()
    temp = dict()
    data = get_data_from_kafka()
    for e in data:
        if e[0] not in mem_yard_info:
            get_yard_info()
        _abbr = mem_yard_info[e[1]]['abbr']
        _loc = mem_yard_info[e[1]]['loc']
        _city = mem_yard_info[e[1]]['city']
        if _city not in ans_json['loc']:
            ans_json['loc'][_city] = _loc
        if _city not in temp:
            temp[_city] = {
                'value': e[2],
                'detail': [{
                    'name': _abbr,
                    'value': e[2]
                }]
            }
        else:
            temp[_city]['value'] += e[2]
            temp[_city]['detail'].append({
                'name': _abbr,
                'value': e[2]
            })

    def merge(l1, l2):
        mid = {}
        for elem in l1 + l2:
            if elem['name'] not in mid:
                mid[elem['name']] = {
                    'name': elem['name'],
                    'value': elem['value']
                }
            else:
                mid[elem['name']]['value'] += elem['value']
        return [v for _, v in mid.items()]

    for k, v in temp.items():
        if k in ans_json['city']:
            ans_json['city'][k]['value'] += v['value']
            ans_json['city'][k]['detail'] = merge(ans_json['city'][k]['detail'], v['detail'])
        else:
            ans_json['city'][k] = {
                'name': k,
                'value': v['value'],
                'detail': v['detail']
            }
    return ans_json


def get_stream_info(request):
    """
    Json Format :
    {
        city: [
            {name: city_name, value: number of boxes in this city, detail: [{name: yard, value: box in this yard}]},
            ...
        ],
        loc: {
            city0: [lng, lat],
            city1: [lng, lat],
            ...
        }
    }
    """
    context = {'city': [], 'loc': {}}
    if request.method == "POST":
        data = virtual_get_stream_data()
        data['city'] = [v for _, v in data['city'].items()]
        return JsonResponse(data)
    else:
        return JsonResponse(context)
