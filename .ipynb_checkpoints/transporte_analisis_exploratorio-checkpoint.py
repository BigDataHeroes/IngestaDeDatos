# # Análisis exploratorio de datos de transporte

import pandas as pd
import json
import numpy as np
from shapely.geometry import shape, Point



def getInputPath():
    return '/'


def getOutputPath():
    return 'transporte.csv'


def getBaseDataPath():
    return '/'


def getOutputAggPath():
  return '/content/drive/My Drive/Output/transporte_agregado.csv'

metro = pd.read_csv(getInputPath() + 'estaciones_metro.csv')
metro['TIPOTRANSPORTE'] = 'Metro'
autobus = pd.read_csv(getInputPath() + 'estaciones_autobus_emt.csv')
autobus['TIPOTRANSPORTE'] = 'Autobus'

transporte = pd.concat([metro, autobus])
transporte.info()


transporte = transporte.loc[:,['BARRIO', 'CODIGOPOSTAL', 'DENOMINACION', 'DISTRITO', 'LATITUD', 'LONGITUD', 'TIPOTRANSPORTE']]
with open(getBaseDataPath() + 'MADRID.geojson') as f:
    js = json.load(f)
    
for index, row in transporte.iterrows():
    point = Point(row['LONGITUD'], row['LATITUD'])
    encontrado = False
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            transporte.loc[index, 'CODIGOPOSTAL'] = float(feature['properties']['COD_POSTAL'])
            encontrado = True
            break
    if not encontrado:
        transporte.loc[index, 'CODIGOPOSTAL'] = np.nan

with open(getBaseDataPath() + 'Barrios.geojson') as f:
    js = json.load(f)
for index, row in transporte.iterrows():
    point = Point(row['LONGITUD'], row['LATITUD'])
    encontrado = False
    for feature in js['features']:
        polygon = shape(feature['geometry'])
        if polygon.contains(point):
            transporte.loc[index, 'BARRIO']=float(feature['properties']['CODBAR'])
            transporte.loc[index, 'DISTRITO']=float(feature['properties']['CODDIS'])
            transporte.loc[index, 'BARRIO_NOMBRE']=str(feature['properties']['NOMBRE'])
            transporte.loc[index, 'DISTRITO_NOMBRE']=str(feature['properties']['NOMDIS'])
            encontrado = True
    if not encontrado:
        transporte.loc[index, 'BARRIO'] = np.nan
        transporte.loc[index, 'DISTRITO'] =np.nan
        transporte.loc[index, 'BARRIO_NOMBRE'] = np.nan
        transporte.loc[index, 'DISTRITO_NOMBRE'] = np.nan

transporte = transporte.dropna()
transporte.to_csv(path_or_buf=getOutputPath(), sep=",")

grouped = datos.groupby(by=['DISTRITO_NOMBRE','DISTRITO','BARRIO_NOMBRE', 'BARRIO', 'TIPOTRANSPORTE'])
datos_agregados = grouped.agg({
                      'DENOMINACION':'count'
                  })
transporte_agregado = datos_agregados.unstack().reset_index()
transporte_agregado.columns = [['DISTRITO_NOMBRE',
 'DISTRITO',
 'BARRIO_NOMBRE',
 'BARRIO',
 'Autobus',
 'Metro']]
transporte_agregado = transporte_agregado.rename(columns={
                      'DISTRITO_NOMBRE':'Distrito_Nombre',
                      'DISTRITO': 'Distrito',
                      'BARRIO_NOMBRE':'Barrio_Nombre',
                      'BARRIO':'Barrio'
                  })
transporte_agregado.to_csv(path_or_buf=getOutputAggPath(), sep=",")

