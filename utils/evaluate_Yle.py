import os
import subprocess
from sklearn.metrics import classification_report
import json
import sys
import numpy as np

for audio_filename in os.listdir("audio_and_annotations/"):
    if audio_filename.endswith(".wav"):
        print(audio_filename)
        annot_file = "audio_and_annotations/annotations_" + audio_filename[:-4] + ".json" 
        process = subprocess.Popen("sh predict_scripts/predict_n_test_yle1.sh audio_and_annotations/" + \
                  audio_filename + " " + annot_file, shell=True, stdout=subprocess.PIPE)
        process.wait()

labels_total = []

for folder in os.listdir("audio_and_annotations/"):
    if os.path.isdir("audio_and_annotations/" + folder):
        path = "/elg/audio_and_annotations/" + folder + "/predict/utt2lang.json"
        res = json.load(open(path))
        labels = sorted(set([k.split('_')[-1]
             for k in res.keys()]).union(set(v for v in res.values())))
        labels_total += labels

labels_total = sorted(set(labels_total))
l2id = {v: i for i, v in enumerate(labels_total)}
id2l = {v: k for k, v in l2id.items()}
pred = []
true = []

for folder in os.listdir("audio_and_annotations/"):
    if os.path.isdir("audio_and_annotations/" + folder):
        path = "audio_and_annotations/" + folder + "/predict/utt2lang.json"
        res = json.load(open(path))

        for k, v in res.items():
            pred.append(l2id[v])
            true.append(l2id[k.split('_')[-1].strip()])

pred, true = np.array(pred), np.array(true)

accuracy = f'Out of {len(pred)} annotations, there are {sum(pred==true)} annotations correctly predicted by memad'

in_details = "\n".join(
    f'There are {sum(p==t==id for p,t in zip(pred,true))} correct {lang} annotations'
    for id, lang in id2l.items())
rp = 'Classification report: ' + classification_report(
    true, pred, target_names=labels_total)

with open('/elg/report.txt', 'w', encoding='utf-8') as f:
    f.write(accuracy + '\n')
    f.write(in_details + '\n')
    f.write(rp)