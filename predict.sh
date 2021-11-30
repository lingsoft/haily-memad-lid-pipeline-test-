# split audio into chunk
WAV="$1"
base=$(dirname $WAV)
main_dir=$(dirname $base)
main_dir=$(dirname $main_dir)
OUTDIR=$base/split


# WAV=/Users/haily/Downloads/memad-lid-pipeline/API/raw/temp.wav
echo "WAV=$WAV"
echo "MAINDIR=$main_dir"

rm -rf $OUTDIR/*.wav
rm -rf $OUTDIR/predict/

echo "\n******************\nSplitting audio file into files of 2 second each\n********************\n"
sh $main_dir/split_wav_to_segments_by2s.sh $WAV $OUTDIR $main_dir
# remove the last line
# echo "\n******************\nRemove the last file which is less than 2 seconds\n********************\n"
# rm -i -- "$(LC_CTYPE=C ls -t $OUTDIR | head -1)"

# 
echo "\n******************\nGenerating uttlabel and uttpath\n********************\n"
if test -f "$maindir/utt2*"; then rm -r $maindir/utt2*; fi
sh $main_dir/generate_utts.sh $OUTDIR

# 
echo "\n******************\nCopy utt* files into new directory predict under $OUTDIR\n********************\n"
mkdir -p $OUTDIR/predict
mv utt2* $OUTDIR/predict/

echo $OUTDIR > paths.txt

# 
echo "\n******************\nRunning prediction\n********************\n"
python3 $main_dir/lid_prediction_pipeline.py $main_dir/resources/prediction_sample.toml paths.txt

