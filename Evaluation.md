## Yle Data evaluation example
The Yle dataset with an experimental license is available upon request [here](https://developer.yle.fi/en/data/avdata/index.html). Dataset 1 contains Audio files (12.7 hours of media), subtitles and ground truth transcripts, speaker diarizations, and NER annotations of 16 factual programs in Finnish and Swedish.

The Yle dataset 1 will have the following structure

```
audios/yle_1/part2
├── audio
│   ├── MEDIA_2014_00868316.utt2label
│   └── MEDIA_2014_00868316.wav
└── readme_and_licence.txt
```

There is a `raw2json` script to convert utt2label format into json format of diarization that memad needs

```
python3 utils/raw2json.py audios/yle_1/part2/audio/MEDIA_2014_00868316.utt2label 
```

After the conversion, the previous directory tree now looks like

```
audios/yle_1/part2
├── anno
│   ├── MEDIA_2014_00868316-diar.json
├── audio
│   ├── MEDIA_2014_00868316
│   ├── MEDIA_2014_00868316.utt2label
│   └── MEDIA_2014_00868316.wav
└── readme_and_licence.txt
```

Then use the `predict_n_test_yle1.sh` bash script to predict and report the classification results of the Yle dataset 1.

```
sh predict_scripts/predict_n_test_yle1.sh audios/yle_1/part2/audio/MEDIA_2014_00868316.wav audios/yle_1/part2/anno/MEDIA_2014_00868316-diar.json
```

Results should be under `report.txt` file.

```
audios/yle_1/part2/audio/MEDIA_2014_00868316/report
└── report.txt
```

Content of report.txt

```
Out of 56 annotations, there are 31 annotations correctly predicted by memad
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
VOX [dev](http://bark.phon.ioc.ee/voxlingua107/dev.zip) dataset contains 1609 speech segments from 33 languages, validated by at least two volunteers. It includes 5 languages that memad lid pipeline supports.
For example, with VOX data structured as follow:
```
audios/VOX
└── dev
    ├── de
    ├── en
    ├── fi
    ├── fr
    └── sv
```
where each subdir contains audios of that language, the directory name is also the label of all audios file inside it.

Run the evaluation on VOX dataset

```
sh predict_scripts/predict_n_test.sh audios/VOX
```

Example result of the Swedish language case

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
