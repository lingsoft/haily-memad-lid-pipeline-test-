import pandas as pd
import datetime
import json
import os
from os.path import dirname as up


def time_convert(x):
    time_obj = datetime.datetime.strptime(x, '%H:%M:%S.%f')
    new_time = "%d.%d"%(3600*time_obj.hour+60*time_obj.minute+time_obj.second, int(time_obj.microsecond/1000))
    return new_time


def utt2label2lang(path):
    df = pd.read_csv(path, sep=' ', names=['name', 'lang'])
    # str2ts = lambda x: x[:-3].replace('0', '') + '.' + x[-3:]
    str2ts = lambda x: int(x)*1.0/1000
    df['start'] = df['name'].map(lambda x: str2ts(x.split('_')[3]))
    df['end'] = df['name'].map(lambda x: str2ts(x.split('_')[4]))
    return df


utt2label_path = os.sys.argv[1]
wav_fname = utt2label_path.split('/')[-1].split('.')[0]
audio_base_dir = up(up(utt2label_path))
anno_diar_path = audio_base_dir + '/anno/' + wav_fname + '-diar.json'

df = utt2label2lang(utt2label_path)

res = []
for index, row in df.iterrows():
    name = row['lang']
    start = str(row['start'])
    end = str(row['end'])
    res.append({'id':name, 'start':start, 'end':end})

print(res)

json.dump(res, open(anno_diar_path, 'w'))
# print(df)

