#!/bin/sh
# Workflow:
  # Work with part1 and part2 of Yle1 dataset
    # Find corresponding WAV file inside audios/yle_1/part2 dir,
    # Look for diar-json file with the format as follows
      # #  [
      # #   {
      # #     "id": "x-nolang",
      # #     "start": "15.0",
      # #     "end": "59.96"
      # #   },
      # #   {
      # #     "id": "x-nolang",
      # #     "start": "60.0",
      # #     "end": "66.96"
      # #   },
      # #   ]
    # Split the audio file according to  diar-json
    # Create new directory with the name of the audio file which contains splited audios, called it `splited audio directory`
      ## Example: split_wav_to_segments.sh audios/yle_2/MEDIA_2009_00001787.wav audios/yle_2/MEDIA_2009_00001787_languageSegments.-diar.json audios/yle_2/MEDIA_2009_00001787
    # Generate meta data utt2path and utt2label
      ## Example: sh generate_utts.sh audios/yle_2/MEDIA_2009_00001787.wav
    # Copy utt2* meta into directory `predict`, of which the splited audios is parent directory. 
    # remove old paths.txt if there is, create a new one with path to `splited audio directory`
    # Run memad pipeline on splited audio directory
      ## Example: python3 lid_prediction_pipeline.py resources/prediction_sample.toml API/paths.txt
    # Calculate metrics with prediction results and store it under report directory - sub dir of `splited audio directory`
      ## Example; python3 evaluation.py audios/yle_1/audio/MEDIA_2009_00001787/predict/utt2lang.json

wav=$1 # 'audios/yle_1/part2/audio/MEDIA_2014_00868316.wav'
anno=$2 # 'audios/yle_1/part2/anno/MEDIA_2014_00868316-diar.json'
# true_label=$3 # 'audios/yle_1/part2/audio/MEDIA_2014_00868316.utt2label'

audio_name=$(basename -- $1)
audio_name="${audio_name%.*}" # should be MEDIA_2014_00868316
audio_dir=$(dirname $wav)/"${audio_name}"

echo "************Split audio file $1 according to annotation json $2 ************\n"
if [ ! -d $audio_dir ]
  then
  echo "Create output audio dir for splited files"
  mkdir $audio_dir
fi
echo "************Saving splited files into $audio_dir************\n"
bash ./utils/split_wav_to_segments.sh $wav $anno $audio_dir

echo "************Generate meta data************\n"
sh ./utils/generate_utts.sh  $audio_dir
mkdir -p $audio_dir/predict
mv utt2* $audio_dir/predict/

echo "************Add audio dir to paths.txt************\n"
rm -rf paths.txt || echo "no paths.txt file to remove"
echo $audio_dir > paths.txt

echo "************Predict labels with memad************\n"
python3 ./utils/lid_prediction_pipeline.py ./resources/prediction_sample.toml paths.txt

echo "************Calculate metrics************\n"
python3 ./utils/evaluation.py $audio_dir/predict/utt2lang.json




