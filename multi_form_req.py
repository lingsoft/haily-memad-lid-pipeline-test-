import os
import json
import requests


def send_request(url, audio, anno=''):

    if anno:
        with open(anno) as json_file:
            anno_lst = json.load(json_file)

        for anno_ in anno_lst:
            anno_["features"] = {"label": anno_.pop("id")}
            anno_["start"] = float(anno_["start"])
            anno_["end"] = float(anno_["end"])
            anno_ = json.dumps(anno_)
        annots = {"lang_segments": anno_lst}
        payload = {
            "type": "audio",
            "format": "LINEAR16",
            "sampleRate": 16000,
            "annotations": annots
        }
    else:
        payload = {"type": "audio", "format": "LINEAR16", "sampleRate": 16000}

    with open(audio, 'rb') as f:
        files = {
            'request': (None, json.dumps(payload), 'application/json'),
            'content': (os.path.basename(audio), f.read(), 'audio/x-wav')
        }

    r = requests.post(url, files=files)
    print(json.dumps(r.json()))


print('Sending request with annotation')
send_request(url='http://localhost:8000/process',
             audio='audios/MEDIA_2014_00868316.wav',
             anno='audios/MEDIA_2014_00868316-diar.json')

# print('Sending request without annotation')
# send_request(url='http://localhost:8000/process',
#              audio='audios/MEDIA_2014_00868316.wav')
