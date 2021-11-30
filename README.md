# Introduction
MeMAD spoken language identification pipeline verification and testing.
Current support languages: fi sv fr de en x-nolang
Input: audio + possible annotation file/diarization json.
Output: spoken language segmentation results
More information about the orignal pipeline is available [here](https://github.com/MeMAD-project/memad-lid-pipeline), models used in the pipeline [here](https://zenodo.org/record/4486873#.YaXpQi0Rr0o)
In general, there are two cases that memad lid pipeline can be tested. 
- Audio file comes with diarization file (timeframe and corresponding spoken language) : this is the best case to evaluate the performance since the tool knows how to split audio file into segments and predict spoken languages of these segmenets
- Audio file only and labels of the whole file. For example Spoken finnish language only audio file.

## General setup
You will need:
- python3.7
- lidbox
- plda
- transfomer
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
Convert utt2label into diarzation that memad needs
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
where each `de` subdir contains audios of that languages, the dir name is also labels of audios inside.

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




