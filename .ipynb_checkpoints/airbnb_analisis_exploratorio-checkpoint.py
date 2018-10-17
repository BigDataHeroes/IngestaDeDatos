
def getInputPath():
  return '/content/drive/My Drive/Input/airbnb.csv'

def getOutputPath():
  return '/content/drive/My Drive/Output/airbnb_clean.csv'

def getBaseDataPath():
  return '/content/drive/My Drive/Base_Data/'

import pandas as pd

datos = pd.read_csv(getInputPath(), sep=',')


"""### Eliminación de columnas"""

datos = datos.iloc[:,37:68]

datos = datos.drop(['square_feet'], axis=1)

datos = datos.drop(["street"], axis = 1)
datos = datos.drop(["neighbourhood"], axis = 1)

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

distritos = pd.read_csv(getBaseDataPath() + "Distritos.csv", sep=";")
datos["neighbourhood_group_cleansed_index"] = datos.neighbourhood_group_cleansed.apply(lambda x: distritos[distritos.Nombre==x].iloc[0,0])
datos = datos.drop(["city"], axis=1)
datos = datos.drop(["state"], axis=1)
datos = datos.drop(["market"], axis=1)
datos = datos.drop(["country_code"], axis=1)
datos = datos.drop(["country"], axis=1)
datos = datos.drop(["smart_location"], axis = 1)

"""### Is location exact"""

datos.is_location_exact.value_counts()

datos.loc[datos.is_location_exact == "t", "is_location_exact"] = 1
datos.loc[datos.is_location_exact == "f", "is_location_exact"] = 0

"""### Property type"""

datos.property_type.value_counts()

import numpy as np
unique_property_type = datos.property_type.unique()
datos["property_type_index"] = datos.property_type.apply(lambda pt: np.where(unique_property_type==pt)[0][0])

"""## Eliminación de columnas"""

datos = datos.drop(["room_type", "accommodates", "bathrooms", "bedrooms", "beds", "bed_type", "amenities", "security_deposit", "cleaning_fee", "guests_included", "extra_people", "minimum_nights"], axis = 1)

"""## Variables de moneda: Conversión a número"""

money_columns = ["price", "weekly_price", "monthly_price"]
for column in money_columns:
    datos.loc[:, column] = datos[column].replace('[\$,]', '', regex=True).astype(float)

"""## Zipcode: Homogenización"""

datos.loc[:, "zipcode"] = datos.zipcode.replace("\n", np.NaN, regex=True).astype('float')

"""## Otras variables: Conversión a categoría"""

datos.loc[:, "property_type"] = datos.property_type.astype('category')
datos.loc[:, "neighbourhood_group_cleansed"] = datos.neighbourhood_group_cleansed.astype('category')
datos.loc[:, "neighbourhood_cleansed"] = datos.neighbourhood_cleansed.astype('category')

"""## Histogramas antes de la limpieza"""

import matplotlib.pyplot as plt # para dibujar
# %matplotlib inline

plt.figure(figsize=(20, 40))
for i, column in enumerate(datos.columns):
    print(column)
    plt.subplot(7,2,i+1)
    if datos[column].dtype.name == 'category':
        datos[column].value_counts().plot(kind='bar')
    else:
        datos[column].plot.hist(alpha=0.5, grid = True)
    plt.xlabel(column)
plt.show()

"""## Outliers: Detección y tratamiento"""

percentiles = datos.quantile([.01, .05, .25, .50, .75, .95, .99, 1])
percentiles

"""### Zipcode"""

!pip install shapely

import json
from shapely.geometry import shape, Point
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

import json
from shapely.geometry import shape, Point
# depending on your version, use: from shapely.geometry import shape, Point

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

"""## Datos nulos: Tratamiento"""

nas_dictionary = {"columns":[], "nas_count":[]}
for column in datos.columns:
    nas_dictionary["columns"].append(column)
    nas_dictionary["nas_count"].append(len(datos[column])-datos[column].count())
nas_dictionary
nas_dataframe = pd.DataFrame(nas_dictionary)
print('Total filas:',len(datos))
nas_dataframe

"""### Zipcode"""

import json
from shapely.geometry import shape, Point
# depending on your version, use: from shapely.geometry import shape, Point

# load GeoJSON file containing sectors
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

"""## Histogramas después del tratamiento"""

import matplotlib.pyplot as plt # para dibujar
# %matplotlib inline

plt.figure(figsize=(20, 40))
for i, column in enumerate(datos.columns):
    plt.subplot(7,2,i+1)
    if datos[column].dtype.name == 'category':
        datos[column].value_counts().plot(kind='bar')
    else:
        datos[column].plot.hist(alpha=0.5, grid = True)
    plt.xlabel(column)
plt.show()

"""## Correlación entre las variables"""

pd.plotting.scatter_matrix(datos, alpha=0.2, figsize=(20, 20), diagonal = 'kde')
plt.show()

"""## Estudio de la variable price por distritos y barrios"""

datos.boxplot(column='price', by='neighbourhood_group_cleansed',figsize=(15,10), rot=45)

datos.loc[:, "neighbourhood_cleansed"] = datos.neighbourhood_cleansed.astype('str')
fig, axes = plt.subplots(11,2,figsize=(20,100)) # create figure and axes

for i, (k, gp) in enumerate(datos.groupby(by=['neighbourhood_group_cleansed'])):
    gp.boxplot(column='price', by='neighbourhood_cleansed', rot=45, ax=axes.flatten()[i])
    axes.flatten()[i].set_title(k)
    fig.suptitle("")
plt.show()

"""## Guardar datos limpios"""

datos.to_csv(path_or_buf=getOutputPath(), sep=",")