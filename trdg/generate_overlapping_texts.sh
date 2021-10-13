#!/bin/bash

create_dir_if_not_exists() {
  if [ ! -d $1 ]; then
    mkdir $1
  fi
}

# check args
while getopts o:i:s: flag
do
    case "${flag}" in
        o) OVERLAP=${OPTARG};;
        i) NUM_ITERATIONS=${OPTARG};;
        s) NUM_SAMPLES=${OPTARG};;
        *) echo "Usage: $0 [-o] (1 or 0) [-i] [-s]" >&2
           exit 1 ;;
    esac
done

# consts
RESULT_DIR='res'
create_dir_if_not_exists "$RESULT_DIR"
OUT_DIR='out'
TEMP_OUT_DIR='out_1'
MAX_MARGIN=20

for ((i=0; i<NUM_ITERATIONS; i++))
do
  create_dir_if_not_exists "$OUT_DIR"
  create_dir_if_not_exists "$TEMP_OUT_DIR"

  # create random values
  WIDTH=$((100 + $RANDOM % 800))
  HEIGHT=$((64 + $RANDOM % 100))
  NUM_WORDS_BACKGROUND=$((1 + $RANDOM % 5))
  MARGIN_TOP=$((0 + $RANDOM % MAX_MARGIN))
  MARGIN_BOTTOM=$((0 + $RANDOM % MAX_MARGIN))
  MARGIN_LEFT=$((0 + $RANDOM % MAX_MARGIN))
  MARGIN_RIGHT=$((0 + $RANDOM % MAX_MARGIN))
  MARGIN=$((0 + $RANDOM % MAX_MARGIN))

  # text generation
  python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c $NUM_SAMPLES -w $NUM_WORDS_BACKGROUND \
    -tc '#000000,#FFFFFF' -obb 3 -ws -b 4 -na 1 -wd $WIDTH -f $HEIGHT --output_dir $TEMP_OUT_DIR -e png \
    -m "$MARGIN_TOP,$MARGIN_LEFT,$MARGIN_BOTTOM,$MARGIN_RIGHT"
  if [[ $OVERLAP == 1 ]]; then
    # generate text on top of generated images with text
    python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c $NUM_SAMPLES \
      -tc '#000000,#FFFFFF' -obb 3 -ws -b 3 -id $TEMP_OUT_DIR -na 1 -f $HEIGHT -e png -wd $WIDTH \
      -m "$MARGIN,$MARGIN,$MARGIN,$MARGIN"
    cp $OUT_DIR/* $RESULT_DIR
  else
    cp $TEMP_OUT_DIR/* $RESULT_DIR
  fi
  rm -rf $OUT_DIR $TEMP_OUT_DIR
done
