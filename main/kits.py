# -*- coding: utf-8 -*-
import os
import json
from geopy.geocoders import Nominatim
from WebApp.settings import BASE_DIR as base
from main.models import YardInfo, ReturnApplyInfo
from django.db.models import Sum
from geopy.exc import GeocoderTimedOut
from datetime import datetime
from threading import Thread
import pykafka
from pykafka import KafkaClient


mem_city_result = dict()
mem_yard_info = dict()
mem_city_loc = dict()
country_info = dict()
city_info = dict()
month_day = 1
kafka_chinarail_data = []
consumer_running = False


def get_address(city, country=''):
    gps = Nominatim()
    query = {'city': city}
    if country != '':
        query['country'] = country
    # print(query)
    try:
        location = gps.geocode(query)
    except GeocoderTimedOut:
        # print(0, 0)
        return 0, 0
    if location:
        # print(location.longitude, location.latitude)
        return location.longitude, location.latitude
    else:
        # print(0, 0)
        return 0, 0


def add_city_data(city, lng, lat, val):
    filename = os.path.join(base, 'static', 'main', 'data', 'map.json')
    with open(filename, 'r', encoding='utf-8') as f:
        origin_data = json.load(f)
    if city not in origin_data['loc']:
        origin_data['city'].append({"name": city, "value": val})
        origin_data['loc'][city] = [lng, lat]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(origin_data, f, indent=1)


def get_city_loc():
    global mem_city_loc
    filename = os.path.join(base, 'static', 'main', 'data', 'city_loc.json')
    with open(filename, 'r', encoding='utf-8') as f:
        mem_city_loc = json.load(f)


def save_city_loc():
    global mem_city_loc
    filename = os.path.join(base, 'static', 'main', 'data', 'city_loc.json')
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(mem_city_loc, f, indent=1)


def get_yard_info():
    objs = YardInfo.objects.all()
    remain = []
    if len(mem_city_loc) == 0:
        get_city_loc()
    flush = False
    for e in objs:
        if e.country == '' or e.city == '':
            remain.append(e)
        elif e.code is not '':
            _city = e.city.strip().split('-')[0]
            _country = e.country
            if _city in mem_city_loc:
                _loc = mem_city_loc[_city]
            else:
                _loc = list(get_address(_city, _country))
                mem_city_loc[_city] = _loc
                flush = True
            if e.code not in mem_yard_info:
                mem_yard_info[e.code] = {
                    'abbr': e.abbr.strip(),
                    'name': e.name.strip(),
                    'city': _city,
                    'country': _country,
                    'loc': _loc
                }
            if e.city_id is not '' and e.city_id not in city_info:
                city_info[e.city_id] = _city
            if e.country_id is not '' and e.country_id not in country_info:
                country_info[e.country_id] = _country
    for e in remain:
        if e.code is not '' and e.code not in mem_yard_info:
            if e.city_id in city_info:
                _city = city_info[e.city_id]
                _country = country_info[e.country_id] if e.country_id in country_info else ''
                _loc = mem_city_loc[_city]
                mem_yard_info[e.code] = {
                    'abbr': e.abbr.strip(),
                    'name': e.name.strip(),
                    'city': _city,
                    'country': _country,
                    'loc': _loc
                }
    if flush:
        save_city_loc()


def consumer_thread():
    global kafka_chinarail_data
    client = KafkaClient(zookeeper_hosts='10.8.4.8:2181')
    topic = client.topics['chinarail']
    consumer = topic.get_balanced_consumer(consumer_group='chinarail', auto_commit_enable=True, zookeeper_connect='10.8.4.8:2181')
    for message in consumer:
        if message is not None:
            try:
                data = message.value.decode('utf-8').strip(',').split(',')
                for elem in data:
                    elem = elem[1:-1].split()
                    if len(elem) > 0:
                        fine = [int(elem[0]), elem[1][1:-1], int(elem[2]), elem[3][11:] + ' ' + elem[4][:8]]
                        print(fine)
                        kafka_chinarail_data.append(fine)
            except Exception as e:
                raise e


def get_data_from_kafka():
    """
    Output: data
    Format: [
        [id, code, number, date]
    ]
    """
    global kafka_chinarail_data
    if not consumer_running:
        thread = Thread(target=consumer_thread)
        thread.start()
    if len(kafka_chinarail_data) > 0:
        data = kafka_chinarail_data.copy()
        kafka_chinarail_data.clear()
    else:
        data = []
    return data


def fake_get_kafka_data():
    global month_day
    res = []
    start_time = str(datetime(2018, 8, month_day, 0, 0))
    month_day = (month_day + 1) % 31 + 1
    end_time = str(datetime(2018, 8, month_day, 0, 0))
    data = ReturnApplyInfo.objects.filter(draw_datetime__gte=start_time)
    data = data.filter(draw_datetime__lte=end_time)
    data = data.values('draw_yard_code').annotate(entries=Sum('container_quantity'))
    _id = 0
    for e in data:
        res.append([_id, e['draw_yard_code'], e['entries']])
        _id += 1
    return res
