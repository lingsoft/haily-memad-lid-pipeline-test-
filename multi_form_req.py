import os
import json
import requests


def send_request(url, audio, anno):
    #payload = {"type":"audio", "format":"LINEAR16","sampleRate":16000, "features":{"fname": os.path.basename(file)}} # send with filename in meta data
    with open(anno) as json_file: 
      anno_lst = json.load(json_file)
    for anno_ in anno_lst:
      anno_["features"]={"label":anno_.pop("id")}
      anno_["start"] = float(anno_["start"])
      anno_["end"] = float(anno_["end"])
      anno_ = json.dumps(anno_)
    annots = {"lang_segments": anno_lst}
    payload = {"type":"audio", "format":"LINEAR16","sampleRate":16000, "annotations":annots}
    #payload = {"type":"audio", "format":"LINEAR16","sampleRate":16000}
    files = {
         'request': (None, json.dumps(payload), 'application/json'),
         'content': (os.path.basename(audio), open(audio, 'rb'), 'audio/x-wav')
    }

    r = requests.post(url, files=files)
    print(json.dumps(r.json()))



# curl -i -X POST -H "Content-Type: multipart/form-data" -F "request={"type":"audio", "format":"LINEAR16","sampleRate":16000}'; headers=Content-Type:application/json" -F "headers=audio/x-wav;content=@MEDIA_2014_00868316.wav"  localhost:3000/process
for i in range(1):
  send_request(url='http://localhost:3000/process', audio='audios/MEDIA_2014_00868316.wav', anno='audios/MEDIA_2014_00868316-diar.json')