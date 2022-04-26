
# Workflow:
# -Loop inside each language dir, 
# -Create corresponding path for each split audios
# -Predicts labels 
# -Compute average accuracy

AUDIO_BASE='audios/'

split_n_predict () {
  WAV_DIR="$1" # Dir with name of label such as audios/VOX/dev/fi/
  MAIN_DIR=$PWD

  echo "WAV_DIR=$WAV_DIR"
  echo "MAINDIR=$MAIN_DIR"

  for f in $WAV_DIR/*.wav
    do
    filename=$(basename -- "$f")
    filename="${filename%.*}"
    # echo "\n******************\nSplitting audio file into files of 2 second each\n********************\n"
    # sh $MAIN_DIR/split_wav_to_segments_by2s.sh $f $WAV_DIR/$filename $MAIN_DIR
    if [[ -f $MAIN_DIR/utt2* ]]
      then 
        rm -rf $MAIN_DIR/utt2* 
    fi
    echo "\n******************\nGenerating uttlabel and uttpath\n********************\n"
    sh $MAIN_DIR/generate_utts.sh  $WAV_DIR/
    mkdir -p $WAV_DIR/predict
    mv utt2* $WAV_DIR/predict
    echo "\n******************\nCopy utt* files into new directory predict under $WAV_DIR/ \n********************\n"
    echo $WAV_DIR/ > paths.txt
    echo "\n******************\nRunning prediction\n********************\n"
    python3 $MAIN_DIR/lid_prediction_pipeline.py $MAIN_DIR/resources/prediction_sample.toml paths.txt
    done
}

# Looping for each language
for f in fi sv de fr en
  do
    if [[ $1 == *"VOX"* ]]; then
      f="${AUDIO_BASE}VOX/dev/${f}"
      echo "lang path $f"
    else
       f="${AUDIO_BASE}CV/${f}"
      echo "lang path $f"
    fi
    split_n_predict $f
  done

# Compute average accuracy
python3 utils/metric_calc.py $1




