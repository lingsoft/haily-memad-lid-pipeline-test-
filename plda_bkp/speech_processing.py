import os
import pandas as pd
import tensorflow as tf
import numpy as np

from lidbox.meta import (
    common_voice,
    generate_label2target,
    verify_integrity,
    read_audio_durations,
    random_oversampling_on_split
)

from lidbox.features import audio, cmvn
import lidbox.data.steps as ds_steps
import scipy.signal

# Init PRNG with fixed seed for reproducibility
import numpy as np
np_rng = np.random.default_rng(1)

languages = ['fi']
datadir = 'fi/cv-corpus-6.1-2020-12-11'

dirs = sorted((f for f in os.scandir(datadir) if f.is_dir()), key=lambda f: f.name)

meta = common_voice.load_all(datadir, languages)
meta, lang2target = generate_label2target(meta)

TF_AUTOTUNE = tf.data.experimental.AUTOTUNE


def metadata_to_dataset_input(meta):
    return {
        "id": tf.constant(meta.index, tf.string),
        "path": tf.constant(meta.path, tf.string),
        "label": tf.constant(meta.label, tf.string),
        "target": tf.constant(meta.target, tf.int32),
        "split": tf.constant(meta.split, tf.string),
        "is_copy": tf.constant(meta.is_copy, tf.bool),
    }


def read_mp3(x):
    s, r = audio.read_mp3(x["path"])
    out_rate = 16000
    s = audio.resample(s, r, out_rate)
    s = audio.peak_normalize(s, dBFS=-3.0)
    s = audio.remove_silence(s, out_rate)
    return dict(x, signal=s, sample_rate=out_rate)


def random_filter(x):
    def scipy_filter(s, N=10):
        b = np_rng.normal(0, 1, N)
        return scipy.signal.lfilter(b, 1.0, s).astype(np.float32), b

    s, _ = tf.numpy_function(
        scipy_filter,
        [x["signal"]],
        [tf.float32, tf.float64],
        name="np_random_filter")
    s = tf.cast(s, tf.float32)
    s = audio.peak_normalize(s, dBFS=-3.0)
    return dict(x, signal=s)


def random_speed_change(ds):
    return ds_steps.random_signal_speed_change(ds, min=0.9, max=1.1, flag="is_copy")


def batch_extract_features(x):
    with tf.device("GPU"):
        signals, rates = x["signal"], x["sample_rate"]
        S = audio.spectrograms(signals, rates[0])
        S = audio.linear_to_mel(S, rates[0])
        S = tf.math.log(S + 1e-6)
        S = cmvn(S, normalize_variance=False)
    return dict(x, logmelspec=S)


def pipeline_from_meta(data, split):
    if split == "train":
        data = data.sample(frac=1, random_state=np_rng.bit_generator)

    ds = (tf.data.Dataset
          .from_tensor_slices(metadata_to_dataset_input(data))
          .map(read_mp3, num_parallel_calls=TF_AUTOTUNE))

    if split == "test":
        return (ds
                .batch(1)
                .map(batch_extract_features, num_parallel_calls=TF_AUTOTUNE)
                .unbatch()
                .cache(os.path.join(cachedir, "data", split))
                .prefetch(1000))
    else:
        return (ds
                .cache(os.path.join(cachedir, "data", split))
                .prefetch(1000)
                .apply(random_speed_change)
                .map(random_filter, num_parallel_calls=TF_AUTOTUNE)
                .batch(1)
                .map(batch_extract_features, num_parallel_calls=TF_AUTOTUNE)
                .unbatch())


cachedir = os.path.join('./', "cache")
os.makedirs(os.path.join(cachedir, "data"))

split2ds = {split: pipeline_from_meta(meta[meta["split"] == split], split)
            for split in meta.split.unique()}
