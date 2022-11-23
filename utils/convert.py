import csv
import os
from pydub import AudioSegment
import datetime
import json
import sys
from sys import platform
import math

def convert_into_seconds(time_str):
    h,m,s = time_str.split(':') # hh:mm:ss,mis
    s = float(s.replace(",", "."))
    return datetime.timedelta(hours=int(h),minutes=int(m),seconds=s).total_seconds()

def convert_lang(lang):
    lang_dict = {"deu": "de", "eng": "en", "eng-GB": "en", "fin": "fi", "fra": "fr", "swe": "sv", "swe-FI": "sv"}
    if lang in lang_dict:
        return lang_dict[lang]
    else:
        return "x-nolang"

def convert_tsv(tsv_file):
    with open(tsv_file) as fd:
        rd = csv.reader(fd, delimiter="\t", quotechar='"')
        annots = []
        for row in rd:
            start = convert_into_seconds(row[0].strip())
            end = convert_into_seconds(row[1].strip())
            lang = convert_lang(row[2].strip())
            annots.append({"id": lang, "start": str(start), "end": str(end)})
    return annots
 
def convert_and_annotate_long_file(filename, sound, tsv_file, annots, chunk_size):
    annot_chunks = []
    n = 0
    while n < len(annots):
        annot_chunks.append(annots[n : n + chunk_size])
        n += chunk_size
    file_n = 1
    saved_files = []
    for annot_chunk in annot_chunks:
        audio_filename = "audio_and_annotations/" + filename + "_" + str(file_n) + ".wav"
        sound[float(annot_chunk[0]["start"]) * 1000 : float(annot_chunk[-1]["end"]) * 1000].\
                export(audio_filename, format="wav", parameters = ['-ar', '16000', '-ac', '1'])
        saved_files.append(audio_filename)
        if os.path.getsize(audio_filename) >= 100000000:
            for f in saved_files:
                os.remove(f)
            return True
        else:
            annots_new = []
            difference = float(annot_chunk[0]["start"]) 
            for x in annot_chunk:
                start_new = str(round(float(x["start"]) - difference, 2))
                end_new   = str(round(float(x["end"])   - difference, 2))
                x["start"] = start_new
                x["end"]   = end_new
                annots_new.append(x)
            json_object = json.dumps(annots_new, indent = 4, ensure_ascii = False)
            annot_filename = "audio_and_annotations/annotations_" + filename + "_" + str(file_n) +".json"
            with open(annot_filename, "w", encoding="utf-8") as outfile:
                outfile.write(json_object)
            saved_files.append(annot_filename)
        file_n += 1
    return False
    
def convert_and_annotate(video_path, tsv_file):
    video_filename = video_path.split("/")[-1][:-4]
    sound = AudioSegment.from_file(video_path, format = "mp4")
    audio_filename = video_filename + ".wav"
    sound.export("audio_and_annotations/" + audio_filename, format="wav", \
                            parameters = ['-ar', '16000', '-ac', '1'])
    annots = convert_tsv(tsv_file)
    if os.path.getsize("audio_and_annotations/" + audio_filename) >= 100000000:
        os.remove("audio_and_annotations/" + audio_filename)
        too_big = True
        chunk_sizes = []
        for i in list(range(len(annots) + 1))[2:]:
            chunk_sizes.append(math.ceil(len(annots)/float(i)))
        chunk_sizes = sorted(set(chunk_sizes), reverse=True)
        n = 0
        while too_big == True and n < len(chunk_sizes):
            too_big = convert_and_annotate_long_file(video_filename, sound, tsv_file, annots, chunk_sizes[n])
            n += 1
    else:
        json_object = json.dumps(annots, indent = 4, ensure_ascii = False)
        annot_filename = "annotations_" + video_filename + ".json"
        with open("audio_and_annotations/" + annot_filename, "w", encoding="utf-8") as outfile:
            outfile.write(json_object)
    
if __name__ == '__main__':
    new_path = "audio_and_annotations/"
    if not os.path.exists(new_path):
       os.makedirs(new_path)
    video_folder = sys.argv[1]
    tsv_folder = sys.argv[2]
    if not video_folder.endswith("/"):
        video_folder += "/"
    if not tsv_folder.endswith("/"):
        tsv_folder += "/"
    for video_filename in os.listdir(sys.argv[1]):
        if video_filename.endswith(".mp4") and video_filename != "MEDIA_2014_00868316.mp4":
            print(video_filename)
            tsv_file = tsv_folder + video_filename[:-4] + ".tsv"
            video_filename = video_folder + video_filename
            convert_and_annotate(video_filename, tsv_file)