import json
from sklearn.metrics import classification_report
import os, fnmatch, sys
import logging

AUDIO_DIR = sys.argv[1]  # 'audios/VOX/dev'
langs = ["sv", "de", "fi", "fr", "en"]
langs_accuracy_dict = {lang: 0.0 for lang in langs}


def process_lang_json(lang, file):
    with open(file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    corr = 0
    for seg, pred in data.items():
        if pred == lang: corr += 1
    num_segment = len(data)
    preds = list(data.values())
    labels = [lang] * num_segment
    return corr * 1.0 / num_segment, num_segment, preds, labels


for lang in langs:
    print('--lang', lang)
    accuracy = 0
    num_segment = 0
    num_segment_ls = []
    utt2lang_json = os.path.join(f"{AUDIO_DIR}/{lang}", "predict",
                                 "utt2lang.json")
    try:
        accuracy, num_segment, preds, labels = process_lang_json(
            lang, utt2lang_json)
    except FileNotFoundError:
        logging.error("Exeption occurred", exc_info=True)
        pass
    langs_accuracy_dict[lang] = accuracy
    num_segment_ls.append(num_segment)
    print('Total audios: ', num_segment)
    print(f'Accuracy: {accuracy:.2f}')
    print('Classification report:')
    print(f'{classification_report(labels,preds,labels=[lang])}\n')
    towrite = f'Total audios: {num_segment}\nAccuracy:\
      {accuracy:.2f}\nClassification report:\n{classification_report(labels,preds,labels=[lang])}'

    with open(f'{AUDIO_DIR}/{lang}_report.txt', 'w') as f:
        f.write(towrite)

print('lang accuracy dict', langs_accuracy_dict)
