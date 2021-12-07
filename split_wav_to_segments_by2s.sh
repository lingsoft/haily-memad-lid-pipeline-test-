#!/bin/sh

# Script for splitting wav file to given segments. 

if [ $# != 3 ]; then
	echo "Usage: ./split_wav_to_segments.sh [WAV_FILE] [OUTPUT_DIR] [MAIN_DIR]  "
	echo ""
	echo "in OUTPUT_DIR."
	exit 1;
fi

WAV="$1"
export OUTDIR="$2"
export MAINDIR="$3"
mkdir -p $OUTDIR


f_name=$(basename -- "$WAV")
f_name="${f_name%.*}"
ffmpeg -i $WAV -f segment -segment_list_type csv -segment_list segments.csv -segment_time 2 -loglevel quiet  -c copy "${OUTDIR}/${f_name}_%02d.wav"

## We have segments.cvs with the following format, let rename the file
#format: MEDIA_2018_01414607_00.wav,0.000000,2.005333

## change name of MEDIA_2018_01414607_722.wav into the format of MEDIA_2018_01414607_722.wav 
python3 $MAINDIR/split_file_map.py $OUTPUT_DIR

