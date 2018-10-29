# -*- coding: utf-8 -*-
import os
import json
from geopy.geocoders import Nominatim
from WebApp.settings import BASE_DIR as base


mem_city_result = dict()


def get_address(city):
    gps = Nominatim()
    location = gps.geocode(city)
    if location:
        return location.longitude, location.latitude
    else:
        return None, None


def add_city_data(city, lng, lat, val):
    filename = os.path.join(base, 'static', 'main', 'data', 'map.json')
    with open(filename, 'r', encoding='utf-8') as f:
        origin_data = json.load(f)
    if city not in origin_data['loc']:
        origin_data['city'].append({"name": city, "value": val})
        origin_data['loc'][city] = [lng, lat]
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(origin_data, f, indent=1)
