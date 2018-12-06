from flask import Flask, request, flash, redirect, url_for, render_template
from sqlalchemy import create_engine
from flask_jsonpify import jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from webserviceutils import security, data
from logging.handlers import RotatingFileHandler
from time import strftime

import pathlib
import pandas as pd
import os
import re
import json
import io
import zipfile
import yaml
import logging
import traceback

# define global variables
script_dir = os.path.dirname(os.path.realpath(__file__))
config = yaml.safe_load(open(os.path.join(script_dir, "config.yml")))
DATA_FOLDER = os.path.join(script_dir, config['data_folder'])
UPLOAD_FOLDER = os.path.join(script_dir, config['upload_folder'])
ALLOWED_IPS = config['allowed_ips']

# Start Flask Server
app = Flask(__name__)

if config['cors']:
    CORS(app)

# LOGGING ASPECTS

@app.after_request
def after_request(response):
    """ Logging after every request. """
    # This avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        ts = strftime('[%Y-%b-%d %H:%M]')
        LOGGER.error('%s %s %s %s %s %s',
                      ts,
                      security.getrequestip(request),
                      request.method,
                      request.scheme,
                      request.full_path,
                      response.status)
    return response

@app.errorhandler(Exception)
def exceptions(e):
    """ Logging after every Exception. """
    ts = strftime('[%Y-%b-%d %H:%M]')
    tb = traceback.format_exc()
    LOGGER.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
                  ts,
                  security.getrequestip(request),
                  request.method,
                  request.scheme,
                  request.full_path,
                  tb)
    return "Internal Server Error", 500

# APP ROUTES

@app.route('/datasets', methods=['GET'])
@security.ipcheck
def get_datasets():
    # regexp for the files in the directory, gives back the matches 'feature', 'position.algorithm', 'schema': ^[\w]+\.(?P<timestamp>[\d]{2}\.[\d]{2}\.[\d]{4})\.(?P<type>feature|position|schema){1}\.?(?P<algorithm>[\D]+)?\.json{1}$
    # included_extensions = ['json']
    relevant_path = DATA_FOLDER
    directories = [fn for fn in os.listdir(relevant_path)]
    regex = re.compile("^[\w]+\.(?P<timestamp>[\w]+)\.(?P<type>feature|position|schema|meta){1}\.?(?P<algorithm>[\w-]+)?\.json{1}$")
    results = []
    for directory in directories:
        regexmatches = {}
        reformattedRegex = {}
        files = [fn for fn in os.listdir(os.path.join(relevant_path, directory))]
        for singlefile in files:
            match = regex.match(singlefile)
            if match:
                regexmatches[singlefile] = match.groupdict()
        for key, value in regexmatches.items():
            if (value['timestamp'] in reformattedRegex):
                if value['type'] in reformattedRegex[value['timestamp']]:
                    if type(reformattedRegex[value['timestamp']][value['type']]) is list:
                        reformattedRegex[value['timestamp']][value['type']].append(value['algorithm'])
                else:
                    reformattedRegex[value['timestamp']][value['type']] = [value['algorithm']]
                # reformattedRegex[value['timestamp']][value['type']] = value['algorithm']
            else:
                reformattedRegex[value['timestamp']] = {}
                reformattedRegex[value['timestamp']][value['type']] = value['algorithm']
        results.append({"Dataset":directory, "Items":[{"Time":k, "Algorithms":v} for k,v in reformattedRegex.items()]})

    return jsonify(results)

@app.route('/datasets/<string:dataset_name>/<string:timestamp>/<string:filetype>', defaults={'algorithm': ""}, methods=['GET'])
@app.route('/datasets/<string:dataset_name>/<string:timestamp>/<string:filetype>/<string:algorithm>', methods=['GET'])
@security.ipcheck
def get_dataset(dataset_name, timestamp, filetype, algorithm):
    if algorithm == "":
        joinlist = (dataset_name, timestamp, filetype, "json")
    else:
        joinlist = (dataset_name, timestamp, filetype, algorithm, "json")
    point = "."
    filename = point.join(joinlist)
    jsonfile = os.path.join(DATA_FOLDER, dataset_name, filename)
    file = io.open(jsonfile, encoding='UTF-8')
    json_data = json.load(file)
    return jsonify(json_data)

@app.route('/', methods=['GET', 'POST'])
@security.ipcheck
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if len(request.files) < 1:
            LOGGER.error('No file part')
            return redirect(request.url)
        for filenr in request.files.to_dict().keys():
            file = request.files.to_dict()[filenr]
            if file.filename == '':
                LOGGER.error('No selected file')
                return redirect(request.url)
            if file and security.allowed_file(file.filename):
                # get appropriate file names
                filename = secure_filename(file.filename)
                datasetname = os.path.splitext(os.path.basename(file.filename))[0]
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                # save file from upload
                file.save(filepath)
                if (pathlib.Path(filepath).suffix == 'zip'):
                    # if its a zip then unzip to data files
                    data.importZip(filepath, os.path.join(DATA_FOLDER, datasetname))
                else:
                    # if its a csv then create data files and migrate content
                    data.importCsv(filepath, DATA_FOLDER)
                # return to datasets
        return_route = config['base_dir'] + 'datasets'
        return redirect(return_route)
    return render_template('upload.html')

# MODULE INIT

if __name__ == '__main__':
    # init logger with Flask App and the logging directory, get its own config?
    handler = RotatingFileHandler(os.path.join(script_dir, "app.log"), maxBytes=100000, backupCount=0)
    LOGGER = logging.getLogger(__name__)
    LOGGER.setLevel(logging.DEBUG)
    LOGGER.addHandler(handler)
    # init security with allowed ip, module needs own config?
    security.init(ALLOWED_IPS)
    app.secret_key = 'IKso8d38JDJ!)jkdsdj'
    app.config['SESSION_TYPE'] = 'filesystem'    
    app.run(port=config['port'])