from functools import reduce
from sklearn.metrics import classification_report
import json
import sys
import os
from os.path import dirname as up
import numpy as np

if __name__ == '__main__':
    path = sys.argv[1]
    res = json.load(open(path))
    # Had to combine all labels from pred and true since each audio file has diff annotations
    labels = sorted(
        set([k.split('_')[-1]
             for k in res.keys()]).union(set(v for v in res.values())))
    l2id = {v: i for i, v in enumerate(labels)}
    id2l = {v: k for k, v in l2id.items()}

    pred = []
    true = []

    for k, v in res.items():
        pred.append(l2id[v])
        true.append(l2id[k.split('_')[-1].strip()])

    pred, true = np.array(pred), np.array(true)
    accuracy = f'Out of {len(pred)} annotations, there are {sum(pred==true)} annotations correctly predicted by memad'

    in_details = "\n".join(
        f'There are {sum(p==t==id for p,t in zip(pred,true))} correct {lang} annotations'
        for id, lang in id2l.items())
    rp = 'Classification report: ' + classification_report(
        true, pred, target_names=labels)

    audio_dir = up(up(path))
    if not os.path.isdir(os.path.join(audio_dir, 'report')):
        os.mkdir(os.path.join(audio_dir, 'report'))

    with open(audio_dir + '/report/report.txt', 'w', encoding='utf-8') as f:
        f.write(accuracy + '\n')
        f.write(in_details + '\n')
        f.write(rp)
