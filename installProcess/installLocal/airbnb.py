# -*- coding: utf-8 -*-

import gzip
import pandas as pd
import sys

reload(sys)
sys.setdefaultencoding('utf-8')
inputF = sys.argv[1]
outputF = sys.argv[2]

with gzip.open(inputF, 'rb') as fichero_descomprimido:
    file_content = fichero_descomprimido.read()
    f2= open(outputF,"wb")
    f2.write(file_content)
    f2.close()
    
