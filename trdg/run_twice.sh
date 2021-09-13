#!/bin/bash

create_dir_if_not_exists() {
  if [ ! -d $1 ];
  then
    mkdir $1
  fi
}

RESULT_DIR='res'
create_dir_if_not_exists "$RESULT_DIR"
OUT_DIR='out'
TEMP_OUT_DIR='out_1'
for i in {1..3}
do
  create_dir_if_not_exists "$OUT_DIR"
  create_dir_if_not_exists "$TEMP_OUT_DIR"
  WIDTH=$((100 + $RANDOM % 800))
  HEIGHT=$((64 + $RANDOM % 100))
  NUM_WORDS_BACKGROUND=$((1 + $RANDOM % 5))
  NUM_WORDS_FOREGROUND=$((1 + $RANDOM % 5))
  MARGIN=$((0 + $RANDOM %10))
  python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c 3 -w $NUM_WORDS_BACKGROUND \
    -tc '#000000,#FFFFFF' -obb 1 -ws -b 4 -na 1 -wd $WIDTH -f $HEIGHT --output_dir $TEMP_OUT_DIR -e png \
    -m "$MARGIN,$MARGIN,$MARGIN,$MARGIN"
  python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c 3 -w $NUM_WORDS_FOREGROUND \
    -tc '#000000,#FFFFFF' -obb 1 -ws -b 3 -id $TEMP_OUT_DIR -na 1 -f $HEIGHT -e png
  cp $OUT_DIR/* $RESULT_DIR
  rm -rf $OUT_DIR $TEMP_OUT_DIR
done
