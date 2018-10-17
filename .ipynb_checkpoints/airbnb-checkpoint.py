# -*- coding: utf-8 -*-

import gzip
import pandas as pd

with gzip.open('airbnb.csv.gz', 'rb') as fichero_descomprimido:
    file_content = fichero_descomprimido.read()
    f2= open('airbnb.csv',"wb")
    f2.write(file_content)
    f2.close()
    


datos = pd.read_csv('airbnb.csv', sep=',')
print(datos.loc[0:10,['neighbourhood','neighbourhood_cleansed','neighbourhood_group_cleansed']])
print(datos.loc[0:10,['city', 'state', 'zipcode' 'market','smart_location']])
print(datos.loc[0:10,[ 'country_code', 'country', 'latitude', 'longitude']])
