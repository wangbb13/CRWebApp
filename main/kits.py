# -*- coding: utf-8 -*-
import os
import json
from geopy.geocoders import Nominatim
from WebApp.settings import BASE_DIR as base
from main.models import YardInfo
from geopy.exc import GeocoderTimedOut


mem_city_result = dict()
mem_yard_info = dict()
mem_city_loc = dict()
country_info = dict()
city_info = dict()


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
