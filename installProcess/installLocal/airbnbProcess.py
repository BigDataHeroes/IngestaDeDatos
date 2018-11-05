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

def deleteColumns(datos):
    datos = datos.iloc[:,37:68]
    datos = datos.drop(["square_feet", "street", "neighbourhood", "city", "state","market","country_code","country", "smart_location",
                    "room_type", "accommodates", "bathrooms", "bedrooms", "beds", "bed_type", "amenities", "security_deposit", "cleaning_fee", "guests_included", "extra_people", "minimum_nights"], axis=1)
    return datos

def homogenizeNeighbourhood(datos):
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
    return datos

def homogenizeNeighbourhoodGroup(datos):
    distritos = pd.read_csv(getBaseDataPath() + "Distritos.csv", sep=";")
    datos["neighbourhood_group_cleansed_index"] = datos.neighbourhood_group_cleansed.apply(lambda x: distritos[distritos.Nombre==x].iloc[0,0])
    return datos


datos = pd.read_csv(getInputPath(), sep=",")

datos = deleteColumns(datos)

datos = homogenizeNeighbourhood(datos)

datos = homogenizeNeighbourhoodGroup(datos)

datos.loc[datos.is_location_exact == "t", "is_location_exact"] = 1
datos.loc[datos.is_location_exact == "f", "is_location_exact"] = 0


unique_property_type = datos.property_type.unique()
datos["property_type_index"] = datos.property_type.apply(lambda pt: np.where(unique_property_type==pt)[0][0])

money_columns = ["price", "weekly_price", "monthly_price"]
for column in money_columns:
    datos.loc[:, column] = datos[column].replace("[\$,]", "", regex=True).astype(float)

datos.loc[:, "zipcode"] = datos.zipcode.replace("\n", np.NaN, regex=True).astype("float")

datos.loc[:, "property_type"] = datos.property_type.astype("category")
datos.loc[:, "neighbourhood_group_cleansed"] = datos.neighbourhood_group_cleansed.astype("category")
datos.loc[:, "neighbourhood_cleansed"] = datos.neighbourhood_cleansed.astype("category")

percentiles = datos.quantile([.01, .05, .25, .50, .75, .95, .99, 1])
percentiles


with open(getBaseDataPath() + "MADRID.geojson") as f:
    js = json.load(f)
for index, row in datos.loc[datos[ "zipcode"] <  percentiles.loc[ 0.01, "zipcode"]].iterrows():
    point = Point(row["longitude"], row["latitude"])
    
    for feature in js["features"]:
        polygon = shape(feature["geometry"])
        if polygon.contains(point):
            datos.loc[index, "zipcode"]=float(feature["properties"]["COD_POSTAL"])

with open(getBaseDataPath() + "MADRID.geojson") as f:
    js = json.load(f)
for index, row in datos.loc[datos[ "zipcode"] >=  percentiles.loc[ 1, "zipcode"]].iterrows():
    point = Point(row["longitude"], row["latitude"])
    for feature in js["features"]:
        polygon = shape(feature["geometry"])
        if polygon.contains(point):
            datos.loc[index, "zipcode"]=float(feature["properties"]["COD_POSTAL"])


datos.loc[datos.price >=  percentiles.price.loc[ 0.99], "price"] = percentiles.price.loc[0.99]
datos.loc[datos.weekly_price >=  percentiles.weekly_price.loc[ 0.99], "weekly_price"] = percentiles.weekly_price[0.99]
datos.loc[datos.monthly_price >=  percentiles.monthly_price.loc[ 0.99], "monthly_price"] = percentiles.monthly_price[0.99]

nas_dictionary = {"columns":[], "nas_count":[]}
for column in datos.columns:
    nas_dictionary["columns"].append(column)
    nas_dictionary["nas_count"].append(len(datos[column])-datos[column].count())
nas_dataframe = pd.DataFrame(nas_dictionary)

with open(getBaseDataPath() + "MADRID.geojson") as f:
    js = json.load(f)
for index, row in datos.loc[datos[ "zipcode"].isna()].iterrows():
    point = Point(row["longitude"], row["latitude"])
    for feature in js["features"]:
        polygon = shape(feature["geometry"])
        if polygon.contains(point):
            datos.loc[index, "zipcode"]=float(feature["properties"]["COD_POSTAL"])

for index, row in datos.loc[datos["weekly_price"].isna()].iterrows():
    datos.loc[index, "weekly_price"] = datos.loc[index, "price"] * 7

for index, row in datos.loc[datos["monthly_price"].isna()].iterrows():
    datos.loc[index, "monthly_price"] = datos.loc[index, "price"] * 30


datos.to_csv(path_or_buf=getOutputPath(), sep=",")

grouped = datos.groupby(by=['neighbourhood_group_cleansed','neighbourhood_group_cleansed_index','neighbourhood_cleansed', 'neighbourhood_cleansed_index'], as_index=False)
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
datos_agregados.to_csv(path_or_buf=getOutputAggPath(), sep=",")
