from pathlib import Path

import pandas as pd

import zipfile
import os
import json
import statistics
import numpy as np
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

class NumpyEncoder(json.JSONEncoder):
    """ Special json encoder for numpy types """
    def default(self, obj): # pylint: disable=E0202
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
            np.int16, np.int32, np.int64, np.uint8,
            np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, 
            np.float64)):
            return float(obj)
        elif isinstance(obj,(np.ndarray,)): #### This is the fix
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def importZip(filepath, extractpath):
    # unzip file from upload
    zip_ref = zipfile.ZipFile(filepath, 'r')
    zip_ref.extractall(extractpath)
    zip_ref.close()
    # delete uploaded zip file
    if os.path.exists(filepath):
        os.remove(filepath)
    # clean uploaded directory
    for root, dirs, files in os.walk(extractpath):
        for file in files:
            myfilepath = os.path.join(root, file)
            myfilename, file_extension = os.path.splitext(myfilepath)
            if file_extension != '.json':
                os.remove(myfilepath)

def importCsv(filepath, extractpath):
    # load data into dataframe
    df_value = pd.read_csv(filepath, sep=';')
    # check on seperator with df.shape
    if (df_value.shape[1] < 3):
        df_value = pd.read_csv(filepath, sep=',')
    if (df_value.shape[1] < 3):
        df_value = pd.read_csv(filepath, sep='\t')
    if (df_value.shape[1] < 3):
        os.remove(filepath)
        raise ValueError('The csv file is not comma, semicolon or tabulator seperated and can not be read.')
    # check on filename structure
    if (len(Path(filepath).stem.split('.')) != 3):
        os.remove(filepath)
        raise ValueError('The csv file name format is wrong.')
    project = Path(filepath).stem.split('.')[0]
    position = Path(filepath).stem.split('.')[1]
    version = Path(filepath).stem.split('.')[2]
    datapath = extractpath + os.sep + project + os.sep

    if not os.path.exists(datapath):
        os.makedirs(datapath)
    else:
        counter = 0        
        while os.path.exists(datapath):
            counter = counter + 1
            datapath = extractpath + os.sep + project + str(counter) + os.sep
        project = project + str(counter)
        os.makedirs(datapath)

    # create positional json
    positionJsonString = '['
    for i in range(0, df_value.shape[0]):
        positionData = {"id": i,"position":{"x": str(df_value['x'][i]).replace(',','.'), "y": str(df_value['y'][i]).replace(',','.')}}
        positionJsonString += json.dumps(positionData, indent=4, sort_keys=True, skipkeys=True, separators=(',', ': '), ensure_ascii=False)
        if (i < df_value.shape[0]-1):
            positionJsonString = positionJsonString + ", "
    positionJsonString += ']'    
    text_file = open(datapath + project + '.' + version + '.position.' + position + '.json', 'w', encoding='utf-8')
    text_file.write(positionJsonString)
    text_file.close()
        
    # prepare feature normalized dataframe and transform cateogrical data to ordinal data
    df_feature = df_value.copy()
    df_feature = df_feature.drop(['x', 'y'], axis=1)
    df_subset = df_feature.select_dtypes(exclude=[np.number])
    header = list(df_feature.iloc[:, :])

    for i in range(0, df_subset.shape[1]):
        label_encoder = LabelEncoder()
        integer_encoded = label_encoder.fit_transform(df_subset.iloc[:,i].replace(np.nan, 'na', regex=True))
        df_feature[df_subset.columns[i]] = integer_encoded

    min_max_scaler = MinMaxScaler()
    df_feature[df_feature.columns] = min_max_scaler.fit_transform(df_feature[df_feature.columns])

    # create feature and value json
    featureJsonString = '['
    # remove x and y columns
    for i in range(0, df_feature.shape[0]):
        values = {}
        features = {}
        for j in range(0, len(header)):
            if (isinstance(df_value.iloc[i, j], str)):
                values[j+1] = df_value.iloc[i, j]
                features[j+1] = str(df_feature.iloc[i,j])
            else:
                values[j+1] = str(df_value.iloc[i, j])
                features[j+1] = str(df_feature.iloc[i, j])
        featureData={"id": i, "values": values, "features": {"1": features}, "default-context": "1"}
        featureJsonString += json.dumps(featureData, indent=4, sort_keys=True, skipkeys=True, separators=(',', ': '), ensure_ascii=False)
        if (i < df_feature.shape[0]-1):
            featureJsonString = featureJsonString + ", "
    featureJsonString += ']'

    text_file = open(datapath + project + '.' + version + '.feature.json', 'w', encoding='utf-8')
    text_file.write(featureJsonString)
    text_file.close()

    # create schema json
    # using first column as color? Now it would be helpful to save the glyph & color & tooltip settings for a dataset.
    schemaData = { 'label' : {}}
    glyph = range(0, len(header))
    for i in range(0, len(header)):
        schemaData['label'][i+1] = header[i]
    schemaData.update({'glyph': [str(i+1) for i in list(glyph)]})
    schemaData.update({'tooltip': [str(i+1) for i in list(glyph)]})
    schemaData.update({'color': "1"})
    schemaData.update({"variant-context": { "1": { "id": "1", "description": "standard context" }}})
    schemaJsonString = json.dumps(schemaData, indent=4, sort_keys=True, skipkeys=True, separators=(',', ': '), ensure_ascii=False)

    text_file = open(datapath + project + '.' + version + '.schema.json', 'w', encoding='utf-8')
    text_file.write(schemaJsonString)
    text_file.close()

    # create metainformation for histograms
    metaJsonData = {}
    steps = 50
    for i in range(0, len(header)):
        histdata = [0] * steps #features are normalized so the steps are 0.1 -> 10 bars
        values = []
        for item in range(0, df_feature.shape[0]):
            value = str(df_feature.iloc[item,i])
            try:
                values.append(float(value))
            except ValueError:
                value = df_feature.iloc[item,i]
                values.append(value)
            index = int(float(value)*steps)
            if index >= steps:
                histdata[steps-1] += 1
            else:
                histdata[index] += 1
        maxi = max(histdata)    
        for k in range(len(histdata)):
            histdata[k] = histdata[k]/maxi
        metaJsonData.update({i+1 : {"histogram": {"%d" % (j): histdata[j] for j in range(0,steps)}, "max": max(values), "min": min(values), "median": statistics.median(values), "variance": statistics.pvariance(values), "deviation": statistics.pstdev(values)}})

    metaJsonString = {"features": metaJsonData}
    text_file = open(datapath + project + '.' + version + '.meta.json', 'w', encoding='utf-8')
    text_file.write(json.dumps(metaJsonString, cls=NumpyEncoder))
    text_file.close()    

    # delete uploaded csv file
    if os.path.exists(filepath):
        os.remove(filepath)