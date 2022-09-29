import subprocess
import os
from pathlib import Path
import json


def predict(audio_save_path, lang_segments_path):
    cur_dir = str(Path(audio_save_path).parents[0])
    fname = Path(audio_save_path).stem  # get only filename, nothing else

    if lang_segments_path is None:  # spliting into 2s chunks
        rc = subprocess.check_call(
            ['sh', 'predict_scripts/predict_2s_chunks.sh', audio_save_path])

        utt2lang_json = f'{cur_dir}/split/predict/utt2lang.json'
        with open(utt2lang_json) as json_file:
            data = json.load(json_file)

        data = dict(
            sorted(data.items(), key=lambda item: item[0].split('_')[3]))

        annotations = {}
        for i, (seg, lang) in enumerate(data.items()):
            annot = {
                "start": 2 * i,
                "end": 2 * i + 2,
                }
            annotations.setdefault(lang, []).append(annot)
        return annotations

    else:  # Segment audio according to annotation and predict
        rc = subprocess.check_call([
            'sh', 'predict_scripts/predict_n_test_yle1.sh', audio_save_path,
            lang_segments_path
        ])

        with open(os.path.join(cur_dir, fname, 'predict',
                               'utt2lang.json')) as json_file:
            data = json.load(json_file)
        
        annotations = {}
        for seg, lang in data.items():
            annot = {
                "start": float(seg.split('_')[0]) * 1.0 / 1000,
                "end": float(seg.split('_')[1]) * 1.0 / 1000,
                "features": {
                    "true_label": seg.split('_')[2]
                }
            }
            annotations.setdefault(lang, []).append(annot)
        return annotations
