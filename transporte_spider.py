# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 09:04:53 2018

@author: Carolina
"""

import requests
import pandas as pd

estaciones_metro_url = 'https://services5.arcgis.com/UxADft6QPcvFyDU1/arcgis/rest/services/Red_Metro/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'
estaciones_autobus_emt_url = 'https://services5.arcgis.com/UxADft6QPcvFyDU1/arcgis/rest/services/M6_Red/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=json'
output_path = ''

request_estaciones_metro = requests.get(estaciones_metro_url)
if request_estaciones_metro.status_code == 200:
    estaciones_metro_json = request_estaciones_metro.json()
    for estacion in estaciones_metro_json['features']:
        estacion['attributes'].update({'LATITUD':estacion['geometry']['y'],'LONGITUD':estacion['geometry']['x']})
    estaciones_metro = [estacion['attributes'] for estacion in estaciones_metro_json['features']  ]
    print(estaciones_metro[0])
    estaciones_metro_df = pd.DataFrame.from_dict(estaciones_metro)
    estaciones_metro_df.to_csv(output_path + 'estaciones_metro.csv', sep=",")
    
request_estaciones_autobus_emt = requests.get(estaciones_autobus_emt_url)
if request_estaciones_autobus_emt.status_code == 200:
    estaciones_autobus_emt_json = request_estaciones_autobus_emt.json()
    for estacion in estaciones_autobus_emt_json['features']:
        estacion['attributes'].update({'LATITUD':estacion['geometry']['y'],'LONGITUD':estacion['geometry']['x']})
 
    estaciones_autobus_emt = [estacion['attributes'] for estacion in estaciones_autobus_emt_json['features']]
    estaciones_autobus_emt_df = pd.DataFrame.from_dict(estaciones_autobus_emt)
    estaciones_autobus_emt_df.to_csv(output_path + 'estaciones_autobus_emt.csv', sep=",")