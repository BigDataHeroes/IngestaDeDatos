# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import json
from shapely.geometry import shape, Point
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
inputF = sys.argv[1]
outputClean = sys.argv[2]
airbnbAgg = sys.argv[3]
baseDataPath = sys.argv[4]

def getInputPath():
    return inputF

def getOutputPath():
    return outputClean

def getBaseDataPath():
    return baseDataPath

def getOutputAggPath():
    return airbnbAgg

datos = pd.read_csv(getInputPath(), sep=',')

datos = datos.drop(columns=['id', 
                            'listing_url',
                            'scrape_id',
                            'thumbnail_url',
                            'medium_url',
                            'xl_picture_url',
                            'host_id',
                            'host_url',
                            'host_name',
                            'host_thumbnail_url',
                            'host_picture_url',
                            'calendar_updated',
                            'calendar_last_scraped',
                            'requires_license',
                            'license',
                            'jurisdiction_names',
                            'is_business_travel_ready',
                            'calculated_host_listings_count',
                            'reviews_per_month'], axis = 1)

"""Vamos a eliminar las variables que tengan menos de un 5% de datos"""
nas_dictionary = {"columns":[], "nas_count":[]}
for column in datos.columns:
    nas_dictionary["columns"].append(column)
    nas_dictionary["nas_count"].append(len(datos[column])-datos[column].count())
nas_dictionary
nas_dataframe = pd.DataFrame(nas_dictionary)

columnas_eliminar = [column for column in nas_dataframe.loc[nas_dataframe.nas_count>len(datos)*0.95, 'columns']]
datos = datos.drop(columns = columnas_eliminar, axis=1)


datos = datos.drop(columns=['experiences_offered'], axis = 1)

"""### picture_url

Lo que nos interesa de esta variable es si hay o no hay foto. Como todas tienen foto no aporta nada así que la eliminamos.
"""

datos = datos.drop(columns=['picture_url'], axis = 1)

"""### host_since

Convertiremos esta variable en numérica calculando los días que lleva siendo anfitrión.
"""

datos.loc[:, 'host_since'] = pd.to_datetime(datos.host_since)

datos['host_since_days'] = datos.host_since.apply(lambda f: (pd.datetime.today() - f).days)

"""### host_location
Eliminaremos esta columna
"""

datos = datos.drop(columns=['host_location'], axis = 1)

"""### host_response_time"""


ctype = CategoricalDtype(categories=["within an hour", "within a few hours", "within a day", "a few days or more"],ordered=True)
datos.loc[:, 'host_response_time'] = datos.host_response_time.astype(ctype)

"""### host_is_superhost"""

dict_boolean= {'t': 1, 'f': 0, np.nan: 0}

datos.loc[:, "host_is_superhost"] = datos.host_is_superhost.apply(lambda x: dict_boolean[x])


"""### host_neighbourhood"""

"""Vamos a eliminar esta columna porque los datos están muy sucios y no tenemos medios para limpiarlos."""

datos = datos.drop(columns = ['host_neighbourhood'], axis = 1)

"""### host_verifications"""

datos.loc[:,'host_verifications']= datos.host_verifications.apply(lambda x: 
                                                                  list(map(lambda y:
                                                                      y.replace("'", "").replace(" ", "")
                                                                      , x[1:-1].split(','))))

verifications_values = set()
for lista in datos.host_verifications:
  
  for valor in lista:
    verifications_values.add(valor)


verifications_values.remove('')
for column in verifications_values:
  datos['host_verification_' + column] = np.nan

for verification_column in verifications_values:
  datos.loc[:,'host_verification_' + verification_column] = datos.host_verifications.apply(lambda lista: int(verification_column in lista))

"""### host_has_profile_pic"""


datos.loc[:, "host_has_profile_pic"] = datos.host_has_profile_pic.apply(lambda x: dict_boolean[x])

"""### host_identity_verified"""


datos.loc[:, "host_identity_verified"] = datos.host_identity_verified.apply(lambda x: dict_boolean[x])

"""### Street"""


"""Esta variable no aporta nada así que la eliminamos"""

datos = datos.drop(["street"], axis = 1)

"""### Neighbourhood"""


"""Esta columna contiene barrios que no existen oficialmente. Utilizaremos la columna neighbourhood_cleansed que contiene los barrios correctos"""

datos = datos.drop(["neighbourhood"], axis = 1)

"""### Neighbourhood_cleansed"""


barrios = pd.read_csv(getBaseDataPath() + "Barrios.csv", sep=";")

datos.loc[datos.neighbourhood_cleansed == "Cármenes","neighbourhood_cleansed"] = "Los Cármenes"
datos.loc[datos.neighbourhood_cleansed == "Rios Rosas","neighbourhood_cleansed"] = "Ríos Rosas"
datos.loc[datos.neighbourhood_cleansed == "Los Angeles","neighbourhood_cleansed"] = "Los Ángeles"
datos.loc[datos.neighbourhood_cleansed == "Aguilas","neighbourhood_cleansed"] = "Las Águilas"
datos.loc[datos.neighbourhood_cleansed == "Zofío","neighbourhood_cleansed"] = "Zofio"
datos.loc[datos.neighbourhood_cleansed == "Apostol Santiago","neighbourhood_cleansed"] = "Apóstol Santiago"
datos.loc[datos.neighbourhood_cleansed == "San Cristobal","neighbourhood_cleansed"] = "San Cristóbal"
datos.loc[datos.neighbourhood_cleansed == "Fuentelareina","neighbourhood_cleansed"] = "Fuentelarreina"

datos["neighbourhood_cleansed_index"] = datos.neighbourhood_cleansed.apply(lambda x: barrios[barrios.Nombre==x].iloc[0,0])


"""### Neighbourhood_group_cleansed"""

distritos = pd.read_csv(getBaseDataPath() + "Distritos.csv", sep=";")

datos["neighbourhood_group_cleansed_index"] = datos.neighbourhood_group_cleansed.apply(lambda x: distritos[distritos.Nombre==x].iloc[0,0])

"""### City"""
"""Esta variable no aporta nada así que la eliminamos"""

datos = datos.drop(["city"], axis=1)

"""### State"""

datos = datos.drop(["state"], axis=1)

"""### Market"""

datos = datos.drop(["market"], axis=1)

"""### Country code"""

datos = datos.drop(["country_code"], axis=1)

"""### Country"""

datos = datos.drop(["country"], axis=1)

"""### Smart location"""

datos = datos.drop(["smart_location"], axis = 1)

"""### Is location exact"""

datos.loc[:, "is_location_exact"] = datos.is_location_exact.apply(lambda x: dict_boolean[x])

"""### Property type"""

datos.loc[:, 'property_type'] = datos.property_type.astype('category')

"""### Room type"""

datos.loc[:, 'room_type'] = datos.room_type.astype('category')

"""### bed_type"""

datos.loc[:, 'bed_type'] = datos.bed_type.astype('category')

"""### Amenities"""

amenities = datos.amenities.apply(lambda x: 
                                            list(map(lambda y:
                                                y.replace('"', "").replace(" ", "_")
                                                , x[1:-1].split(','))))

amenities_values = set()
for lista in amenities:
  for valor in lista:
    amenities_values.add(valor)

amenities_values.remove('')
for column in amenities_values:
  datos['amenities_' + column] = np.nan

for amenities_column in amenities_values:
  datos.loc[:,'amenities_' + amenities_column] = amenities.apply(lambda lista: int(amenities_column in lista))

"""### has_availability"""

datos.loc[:, "has_availability"] = datos.has_availability.apply(lambda x: dict_boolean[x])

"""### cancellation_policy"""

datos.loc[:,'cancellation_policy'] = datos.cancellation_policy.astype('category')

"""## Eliminación de columnas"""

datos = datos.drop(['number_of_reviews', 'first_review', 'last_review',
       'review_scores_rating', 'review_scores_accuracy',
       'review_scores_cleanliness', 'review_scores_checkin',
       'review_scores_communication', 'review_scores_location',
       'review_scores_value', 'instant_bookable', 
       'require_guest_profile_picture', 'require_guest_phone_verification'], axis = 1)

"""## Variables de moneda: Conversión a número"""

money_columns = ["price", "weekly_price", "monthly_price", "extra_people","security_deposit", "cleaning_fee"]
for column in money_columns:
    datos.loc[:, column] = datos[column].replace('[\$,]', '', regex=True).astype(float)

"""## Zipcode: Homogenización"""

datos.loc[:, "zipcode"] = datos.zipcode.replace("\n", np.NaN, regex=True).astype('float')

"""## Otras variables: Conversión a categoría"""

datos.loc[:, "neighbourhood_group_cleansed"] = datos.neighbourhood_group_cleansed.astype('category')
datos.loc[:, "neighbourhood_cleansed"] = datos.neighbourhood_cleansed.astype('category')

text_columns = ["name", "summary", "space", "description", "neighborhood_overview", "notes", "transit", "access", "interaction", "house_rules", "host_about", "amenities"]
dict_text_columns = {column: 's_' + column for column in text_columns}
datos = datos.rename(columns=dict_text_columns)

date_columns = ["last_scraped", "host_since"]
dict_date_columns = {column: 'd_' + column for column in date_columns}
datos = datos.rename(columns=dict_date_columns)

other_columns = ["host_response_rate", "host_verifications"]
dict_other_columns = {column: 'd_' + column for column in other_columns}
datos = datos.rename(columns=dict_other_columns)

"""## Outliers: Detección y tratamiento"""

percentiles = datos.quantile([.01, .05, .25, .50, .75, .95, .99, 1])
percentiles

"""### Zipcode"""

# depending on your version, use: from shapely.geometry import shape, Point

# load GeoJSON file containing sectors
with open(getBaseDataPath() + 'MADRID.geojson') as f:
    js = json.load(f)
for index, row in datos.loc[datos[ 'zipcode'] <  percentiles.loc[ 0.01, 'zipcode']].iterrows():
    # construct point based on lon/lat returned by geocoder
    point = Point(row['longitude'], row['latitude'])
    
    # check each polygon to see if it contains the point
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            datos.loc[index, 'zipcode']=float(feature['properties']['COD_POSTAL'])

# load GeoJSON file containing sectors
with open(getBaseDataPath() + 'MADRID.geojson') as f:
    js = json.load(f)
for index, row in datos.loc[datos[ 'zipcode'] >=  percentiles.loc[ 1, 'zipcode']].iterrows():
    # construct point based on lon/lat returned by geocoder
    point = Point(row['longitude'], row['latitude'])
    # check each polygon to see if it contains the point
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            datos.loc[index, 'zipcode']=float(feature['properties']['COD_POSTAL'])

"""### Prices"""

datos.loc[datos.price >=  percentiles.price.loc[ 0.99], 'price'] = percentiles.price.loc[0.99]

datos.loc[datos.weekly_price >=  percentiles.weekly_price.loc[ 0.99], 'weekly_price'] = percentiles.weekly_price[0.99]

datos.loc[datos.monthly_price >=  percentiles.monthly_price.loc[ 0.99], 'monthly_price'] = percentiles.monthly_price[0.99]

with open(getBaseDataPath() + 'MADRID.geojson') as f:
    js = json.load(f)
for index, row in datos.loc[datos[ 'zipcode'].isna()].iterrows():
    # construct point based on lon/lat returned by geocoder
    point = Point(row['longitude'], row['latitude'])
    # check each polygon to see if it contains the point
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            datos.loc[index, 'zipcode']=float(feature['properties']['COD_POSTAL'])

"""### Prices"""

for index, row in datos.loc[datos['weekly_price'].isna()].iterrows():
    datos.loc[index, 'weekly_price'] = datos.loc[index, 'price'] * 7

for index, row in datos.loc[datos['monthly_price'].isna()].iterrows():
    datos.loc[index, 'monthly_price'] = datos.loc[index, 'price'] * 30


"""## Guardar datos limpios"""

datos.to_csv(path_or_buf=getOutputPath(), sep=",")

"""## Agregación de datos por barrios"""

datos_limpios = pd.read_csv(getOutputPath())


grouped = datos_limpios.groupby(by=['neighbourhood_group_cleansed','neighbourhood_group_cleansed_index','neighbourhood_cleansed', 'neighbourhood_cleansed_index'], as_index=False)

import numpy as np
datos_agregados = grouped.agg({
                      'price':np.mean,
                      'weekly_price':np.mean,
                      'monthly_price':np.mean,
                      'zipcode':'count'
                  }).rename(columns={
                      'zipcode':'Cuenta',
                      'neighbourhood_group_cleansed':'Distrito_Nombre',
                      'neighbourhood_cleansed':'Barrio_Nombre',
                      'neighbourhood_cleansed_index':'Barrio',
                      'property_type':'Tipo_propiedad',
                      'price': 'Precio_noche',
                      'weekly_price': 'Precio_semana',
                      'monthly_price':'Precio_mes'
                  })
datos_agregados

"""## Guardar datos agregados"""

datos_agregados.to_csv(path_or_buf=getOutputAggPath(), sep=",")