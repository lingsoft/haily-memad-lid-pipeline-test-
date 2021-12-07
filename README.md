# Introduction
MeMAD spoken language identification (LID) pipeline verification and testing\
Current support languages: fi sv fr de en x-nolang\
Input: audio + annotation file/diarization json\
Output: spoken language segmentation results\
Credits and more information about the original pipeline is available [here](https://github.com/MeMAD-project/memad-lid-pipeline), models used in the pipeline [here](https://zenodo.org/record/4486873#.YaXpQi0Rr0o)\
In general:
- Pass input audio into diarization and ASR system to obtain audio segmentation according to speaker changes
- Audio file and diarization file then goes to the Memad LID pipeline, output is ELG json response which contains identified languages of different segments and also Memad performance report.

## General setup
You will need:
- python3.7
- lidbox
- plda
- transformer
- memad lid models [here](https://zenodo.org/record/4486873#.YaXpQi0Rr0o)

Install dependencies
```shell
python3 -m venv venv && source venv/bin/activate
pip install -r requiremets.txt
```

Install Lidbox
```shell
pip install lidbox -e git+https://github.com/py-lidbox/lidbox.git@e60d5ad2ff4d6076f9afaa780972c0301ee71ac8#egg=lidbox
```

Install plda
```shell
cd plda_bkp
pip install .
```

Install tensorflow
```shell
pip install tensorflow
```

## Yle Data evaluation:
If you are interested in Yle dataset with an experimental license, reference [here](https://developer.yle.fi/en/data/avdata/index.html)

Yle data contain audio + diarization in json format.

Take example for an audio file with name MEDIA_2014_00868316.wav 

YLE1 data set should have the following structure
```shell
audios/yle_1/part2
├── audio
│   ├── MEDIA_2014_00868316.utt2label
│   └── MEDIA_2014_00868316.wav
└── readme_and_licence.txt
```
Convert utt2label into diarization that memad needs
```shell
python3 raw2json.py audios/yle_1/part2/audio/MEDIA_2014_00868316.utt2label 
```
Previous dir tree should look like
```shell
audios/yle_1/part2
├── anno
│   ├── MEDIA_2014_00868316-diar.json
├── audio
│   ├── MEDIA_2014_00868316
│   ├── MEDIA_2014_00868316.utt2label
│   └── MEDIA_2014_00868316.wav
└── readme_and_licence.txt
```
`MEDIA_2014_00868316-diar.json` is converted from true label file `MEDIA_2014_00868316.utt2label` using `raw2json.py` with the following script:

Run prediction pipeline with 2 arguments: input audio file and its corresponding annotation file for splitting. 
```shell
sh predict_n_test_yle1.sh audios/yle_1/part2/audio/MEDIA_2014_00868316.wav audios/yle_1/part2/anno/MEDIA_2014_00868316-diar.json
```
Results should be under `report.txt` report file.
```shell
audios/yle_1/part2/audio/MEDIA_2014_00868316/report
└── report.txt
```
Content of report.txt
```
Out of 56 annotations, there are 31 annotation correctly predicted by memad
There are 0 correct de annotations
There are 0 correct en annotations
There are 23 correct fi annotations
There are 6 correct sv annotations
There are 2 correct x-nolang annotations
              precision    recall  f1-score   support

          de       0.00      0.00      0.00         0
          en       0.00      0.00      0.00         0
          fi       0.77      0.79      0.78        29
          sv       0.75      0.32      0.44        19
    x-nolang       0.67      0.25      0.36         8

    accuracy                           0.55        56
   macro avg       0.44      0.27      0.32        56
weighted avg       0.75      0.55      0.61        56
```

## VOX dev data evaluation
VOX [dev](http://bark.phon.ioc.ee/voxlingua107/dev.zip)
This development set (dev.zip) contains 1609 speech segments from 33 languages, validated by at least two volunteers to really contain the given language.
We took out only 5 languages that Memad-lid project supports.
For example with VOX data structure as follow:
```shell
audios/VOX
└── dev
    ├── de
    ├── en
    ├── fi
    ├── fr
    └── sv
```
where each `de` subdir contains audios of that language, the dir name is also labels of audios inside.

```shell
sh predict_n_test.sh audios/VOX
```
Result of Swedish case
```
--lang sv
Total audios:  100
Accuracy: 0.49
Classification report:
              precision    recall  f1-score   support

          sv       1.00      0.49      0.66       100

   micro avg       1.00      0.49      0.66       100
   macro avg       1.00      0.49      0.66       100
weighted avg       1.00      0.49      0.66       100
```

# MEMAD pipeline API Service, ELG compatible

## Introduction
Spoken Language Identification API compatible with [ELG](https://european-language-grid.readthedocs.io/en/latest/all/A2_API/LTInternalAPI.html#audio-requests)

## Start API service
```shell
export FLASK_APP=app
flask run --host 0.0.0.0 --port <port>
```
Optional:
putting in debug mode with 
```shell
export FLASK_ENV=development
```

## API Endpoints Description, follow ELG format
with WAV format input audio
### Audio Request 
More about ELG required multipart/form-data API request in [multi_form_req.py](multi_form_req.py)
POST requests in the following structure
```json
{
  "type":"audio",
  "params":{...}, // optional
  "format":"string", // LINEAR16 for WAV
  "sampleRate":number, // 16000
  "features":{ /* arbitrary JSON metadata about this content, optional */ },
  "annotations":{ /* optional */
    "<annotation type>":[
      {
        "start":number,
        "end":number,
        "features":{ /* arbitrary JSON */ }
      }
    ]
  }
}
```
MeMAD API supports `LINEAR16` audio format with `16000`sample rate
### Successful response
Annotation response from the API which splits input audio into every 2 seconds chunk and predict spoken languages (fi, sv, de, fr, x-nolang,)
```json
{
   "response":{
      "type":"annotations",
      "annotations":{
         "spoken_language_identification":[
            {
               "start":0,
               "end":2,
               "features":{
                  "SLI":"fi"
               }
            },
            {
               "start":2,
               "end":4,
               "features":{
                  "SLI":"fi"
               }
            },
            {
               "start":4,
               "end":6,
               "features":{
                  "SLI":"fi"
               }
            },
            {
               "start":6,
               "end":8,
               "features":{
                  "SLI":"fi"
               }
            },
            {
               "start":8,
               "end":10,
               "features":{
                  "SLI":"fi"
               }
            },
            {
               "start":10,
               "end":12,
               "features":{
                  "SLI":"fi"
               }
            },
            {
               "start":12,
               "end":14,
               "features":{
                  "SLI":"fi"
               }
            },
            {
               "start":14,
               "end":16,
               "features":{
                  "SLI":"fi"
               }
            },
            {
               "start":16,
               "end":18,
               "features":{
                  "SLI":"fi"
               }
            }
         ]
      }
   }
}
```

### Failure response
 ```json
{
  "failure":{
    "errors":[
      {
        "code":"elg error type code",
        "text":"elg error type related text",
        "params":[],
        "detail":{"Some detail error msg"}
      },
    ]
  }
}
```
with WAV format input audio + annotation json file
### Audio request
```shell
python3 multi_form_req.py
```
The script sends multipart/form-data POST request with the audio file `MEDIA_2014_00868316.wav` and annotation json `MEDIA_2014_00868316-diar.json`.
Example annotation file
```json
[
  {
    "id": "x-nolang",
    "start": "4.15",
    "end": "4.92"
  },
  {
    "id": "x-nolang",
    "start": "15.73",
    "end": "16.29"
  },
  {
    "id": "x-nolang",
    "start": "20.39",
    "end": "20.78"
  },
  {
    "id": "sv",
    "start": "23.36",
    "end": "25.235"
  },
  {
    "id": "fi",
    "start": "25.235",
    "end": "26.735"
  },
]
```


### Successful response (truncated)
```json
{
   "response":{
      "type":"annotations",
      "annotations":{
         "spoken_language_identification":[
            {
               "start":4.15,
               "end":4.92,
               "features":{
                  "LID":"en",
                  "true_label":"x-nolang"
               }
            },
            {
               "start":15.73,
               "end":16.29,
               "features":{
                  "LID":"x-nolang",
                  "true_label":"x-nolang"
               }
            },
            {
               "start":20.39,
               "end":20.78,
               "features":{
                  "LID":"x-nolang",
                  "true_label":"x-nolang"
               }
            },
            {
               "start":23.36,
               "end":25.235,
               "features":{
                  "LID":"x-nolang",
                  "true_label":"sv"
               }
            },
            {
               "start":25.235,
               "end":26.735,
               "features":{
                  "LID":"en",
                  "true_label":"fi"
               }
            },
         ],
         "reports":[
            {
               "start":0,
               "end":99999,
               "features":{
                  "report":"Out of 56 annotations, there are 31 annotation correctly predicted by memad\nThere are 0 correct de annotations\nThere are 0 correct en annotations\nThere are 23 correct fi annotations\nThere are 6 correct sv annotations\nThere are 2 correct x-nolang annotations\n              precision    recall  f1-score   support\n\n          de       0.00      0.00      0.00         0\n          en       0.00      0.00      0.00         0\n          fi       0.77      0.79      0.78        29\n          sv       0.75      0.32      0.44        19\n    x-nolang       0.67      0.25      0.36         8\n\n    accuracy                           0.55        56\n   macro avg       0.44      0.27      0.32        56\nweighted avg       0.75      0.55      0.61        56\n"
               }
            }
         ]
      }
   }
}
```


## To use the API with docker
### Build the docker image
```shell
docker build . -t memad-api
```
### Run the docker based on recent created image tagged with name: memad-api
```shell
docker run --rm -p 3000:8000 memad-api
```
### Test the docker container
```shell
python3 elg_test.py
```


