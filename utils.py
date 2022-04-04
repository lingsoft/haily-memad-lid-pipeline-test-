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

        results = [{
            "start": 2 * i,
            "end": 2 * i + 2,
            "features": {
                "lang": lang
            }
        } for i, (seg, lang) in enumerate(data.items())]

        return {"spoken_language_identification": results}

    else:  # Segment audio according to annotation and predict
        rc = subprocess.check_call([
            'sh', 'predict_scripts/predict_n_test_yle1.sh', audio_save_path,
            lang_segments_path
        ])

        with open(os.path.join(cur_dir, fname, 'predict',
                               'utt2lang.json')) as json_file:
            data = json.load(json_file)

        results = [{
            "start": int(seg.split('_')[0]) * 1.0 / 1000,
            "end": int(seg.split('_')[1]) * 1.0 / 1000,
            "features": {
                "lang": lang,
                "true_label": seg.split('_')[2]
            }
        } for seg, lang in data.items()]

        # reporting about performance, since we have true labels
        with open(os.path.join(cur_dir, fname, 'report', 'report.txt'),
                  'r') as rp:
            report = rp.read()

        report_obj = {
            "start": int(results[0]["start"]),
            "end": int(results[-1]["end"]),
            "features": {
                "report": report
            }
        }

        return {
            "spoken_language_identification": results,
            "reports": [report_obj]
        }
