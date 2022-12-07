# Glyphboard Backend Documentation
 
A small python backend implementing Glyphboard API

## Setup

Download and install [Python 3.6](https://www.python.org/downloads/).

Using PIP tools for dependencies (see [Documentation](https://pip.pypa.io/en/stable/user_guide/#id1)):

````
$ pip install --upgrade pip        # pip-tools needs pip==6.1 or higher (!)
$ pip install pip-tools            # required once 
$ pip install -r requirements.txt  # main command
...
$ pip freeze > requirements.txt    # run after adding new libraries and commit 
````

## Configuration

The server is configured via a `config.yml`. 

````yaml
base_dir: /         # hosting with subdirectories
data_folder: data   # the folder where data is kept
upload_folder: data # folder for uploading data
port: 4201          # port for backend
cors: on            # allow cross-origin calls
allowed_ips:        # whitelisting of allowed uploaders
  - 127.0.0.1       # leave empty to allow all
  - ...
````

## Run

This project is added to the main repository of Glyphboard as a submodule. There is a npm configuration which starts this backend server and Glyphboard. For standalone tests you may start the server with:

````
$ python server.py
````

The server will be at port 4201.

## Data Import via CSV

Using a POST request to the base URL of the backend '/' CSV files can be uploaded and automatically converted to the necessary JSON files (see below). CSV files must adhere to a specific naming scheme and layout.

### File Naming

Uploaded CSV files must use the following naming convention:

`<datasetname>.<positionalgorithm>.<version>`

Where `<datasetname>` is replaced with the name of the dataset, later used to select this data set. `<positionalalgorithm>` will be used to name the position file created for this data set and should reflect the algorithm used to provide the positional data in the CSV file. `<version>` is an arbitrary string describing the version of the data (do not use dots, hyphens, etc.). Note that multiple uploads will result in copies of the data set and not update the versions within a previously uploaded file!

Example: `myglyphboarddata.pca.20201210.csv`

### CSV Layout

CSV files use a header to describe the contained data. Use one line for each data point, where the first column must be named `id` and contain the numerical ID of the data point. The following columns can contain an arbitrary number of dimensions / features of the data point. The last two columns must be named `x` and `y` respectively and contain numerical coordinates for the two-dimensional plot in Glyphboard.

Example:

| id  | text                  | ...   | x      | y       |
|-----|-----------------------|-------|--------|---------|
| 1   | Lorem ipsum           |       | 231.2  | 12.1    |
| 2   | Text of a data point  |       | 72.1   | 102.2   |
| 3   | Another text data     |       | -45.9  | 200.75  |
| .   | .                     |       | .      | .       |
| .   | .                     |       | .      | .       |
| .   | .                     |       | .      | .       |

## Definition of JSON API

The API relies on several files with a defined naming schema:

* `titel.timestamp.schema.json`
    * labels of features
    * extension point for meta-information
* `titel.timestamp.position.mds.json`
    * position in n-dimensions (1-3)
* `titel.timestamp.feature.json`
    * raw values
    * feature space
* `titel.timestamp.meta.json`
    * calculated histograms for each feature across the whole data set
    * min, max, deviation, etc. values for each feature across the whole data set
* timestamp allows the comparison of different points in time, e.g. `24122018`
* mds allows for comparison of different positioning algorithms
* count of Data-Items needs to be the same in feature and position files
* REST-Service is in the backend of the glyphboard

### `titel.timestamp.schema.json`
```JSON
{
    "glyph": [ /* Contains all features (IDs) used */
        "1",   /* for the glyph visualization */
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9"
    ],
    "tooltip": [ /* Contains all features (IDs) */ 
        "1",     /* displayed in the tooltip */
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "11"
    ],
    "label": { /* Human readable descriptions of all features */
        "1": "description",
        "2": "feature",
        "3": "keywords",
        "4": "manufacturer_id",
        "5": "manufacturer_name",
        "6": "name",
        "7": "ean",
        "8": "article_id",
        "9": "catalog_id",
        "10": "cluster_id",
        "11": "distance_to_clusterrep"
    },
    "color": "9",        /* ID of feature for color coding */
    "variant-context": [ /* Each item has different feature variants */
		{
			"id": "1",              /* ID of context */
            "description": "Berechnungsvorschrift A",
                                    /* human readable description 
                                    /* for context */
            "highlight-item": "123" /* optional item ID for */
                                    /* highlighting in visualization */
		},
		{
			"id": "2",
			"description": "Berechnungsvorschrift B",			
			"highlight-item": "156"
		}		
	]
}
```
### `titel.timestamp.feature.json`
```JSON
{
    "features": { /* Calculated feature values */
        "1": { /* Feature context with variant ID 1 */
            "1": 0.4998870908835737,
            "2": 0.45877504818034287,
            "3": 0.9282432474959494,
            "4": 0,
            "5": 0,
            "6": 0.2909703073454401,
            "7": 0,
            "8": "na",
            "9": "na"
        },
        "2": { /* Feature context with variant ID 2 */
            "1": 0.4998870908835737,
            "2": 0.45877504818034287,
            "3": 0.9282432474959494,
            "4": 0,
            "5": 0,
            "6": 0.2909703073454401,
            "7": 0,
            "8": "na",
            "9": "na"
        },
        "global": { /* Global features are equal for */
                    /* all variants above (redundant) */
            "10": 3,
            "11": 0.0
        }
    },
    "values": { /* Plain values for all features */
        "1": "Innen-Sechskant-Schraubendreher-Einsatz etc pp",
        "2": "na",
        "3": "4000896039388>Hazet>8801-5",
        "4": "8801-5",
        "5": "Hazet",
        "6": "Innen-Sechskant Steckschlüssel-Bit",
        "7": "4000896039388",
        "8": "804980-BP",
        "9": "B4494",
        "10": 3,
        "11": 0
    },
    "id": 0, /* Unique ID of the item */
    "default-context":2 /* Default variant context */
}
```
### `titel.timestamp.position.mds.json`

```JSON
{
    "id": 0,
    "position": {
        "x": "9.07479457327",
        "y": "-0.964872467631"
    }
},
{
    "id": 1,
    "position": {
        "x": "6.29459747254",
        "y": "7.38385281322"
    }
},
{
    "id": 2,
    "position": {
        "x": "-6.28191614046",
        "y": "-0.379292186619"
    }
}
```

### `titel.timestamp.meta.json`

```JSON
{
  "features": {
    "2": {
      "histogram": {
        "0": 1.0,
        "1": 0.018037363109297832,
        "2": 0.01245436976594374,
        "3": 0.038222031350654925,
        "4": 0.009448142581060769,
        "5": 0.013957483358385226,
        "6": 0.011595447713120034,
        "7": 0.0055829933433540905,
        "8": 0.004724071290530384,
        "9": 0.0070861069357955764,
        "10": 0.0032209576980888983,
        "11": 0.0017178441056474125,
        "12": 0.0032209576980888983,
        "13": 0.0008589220528237063,
        "14": 0.00042946102641185313,
        "15": 0.002147305132059266,
        "16": 0.0,
        "17": 0.0006441915396177797,
        "18": 0.0012883830792355595,
        "19": 0.0,
        "20": 0.00021473051320592657,
        "21": 0.00021473051320592657,
        "22": 0.0,
        "23": 0.00021473051320592657,
        "24": 0.00042946102641185313,
        "25": 0.0006441915396177797,
        "26": 0.0006441915396177797,
        "27": 0.00042946102641185313,
        "28": 0.0,
        "29": 0.0,
        "30": 0.0,
        "31": 0.0008589220528237063,
        "32": 0.0,
        "33": 0.0,
        "34": 0.0,
        "35": 0.0,
        "36": 0.0,
        "37": 0.0,
        "38": 0.0,
        "39": 0.0,
        "40": 0.0,
        "41": 0.0,
        "42": 0.0,
        "43": 0.00021473051320592657,
        "44": 0.0,
        "45": 0.0,
        "46": 0.0,
        "47": 0.0,
        "48": 0.0,
        "49": 0.00021473051320592657
      },
      "max": 1.0,
      "min": 0.0,
      "median": 0.0,
      "variance": 0.0029337554579717175,
      "deviation": 0.05416415288704991
    },
    "3": {
      "histogram": {
        "0": 0.3810483870967742,
        "1": 0.04435483870967742,
        "2": 0.04032258064516129,
        ...
      }
    },
    ...
  }
}
```
