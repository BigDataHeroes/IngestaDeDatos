#!/bin/bash

source activate keepcodingFinalProject
source properties.sh

python airbnbProcess.py $airbnbOutput $airbnbClean $airbnbAgg $baseDataPath
