#!/bin/bash

create_dir_if_not_exists() {
  if [ ! -d $1 ];
  then
    mkdir $1
  fi
}

OVERLAP=1
RESULT_DIR='res'
create_dir_if_not_exists "$RESULT_DIR"
OUT_DIR='out'
TEMP_OUT_DIR='out_1'
NUM_SAMPLES=3
MAX_MARGIN=30
for i in {1..3}
do
  create_dir_if_not_exists "$OUT_DIR"
  create_dir_if_not_exists "$TEMP_OUT_DIR"
  WIDTH=$((100 + $RANDOM % 800))
  HEIGHT=$((64 + $RANDOM % 100))
  NUM_WORDS_BACKGROUND=$((1 + $RANDOM % 5))
  MARGIN_TOP=$((0 + $RANDOM % MAX_MARGIN))
  MARGIN_BOTTOM=$((0 + $RANDOM % MAX_MARGIN))
  MARGIN_LEFT=$((0 + $RANDOM % MAX_MARGIN))
  MARGIN_RIGHT=$((0 + $RANDOM % MAX_MARGIN))
  MARGIN=$((0 + $RANDOM % MAX_MARGIN))
  python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c $NUM_SAMPLES -w $NUM_WORDS_BACKGROUND \
    -tc '#000000,#FFFFFF' -obb 3 -ws -b 4 -na 1 -wd $WIDTH -f $HEIGHT --output_dir $TEMP_OUT_DIR -e png \
    -m "$MARGIN_TOP,$MARGIN_LEFT,$MARGIN_BOTTOM,$MARGIN_RIGHT"
  if [[ $OVERLAP == 1 ]]; then
    python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c $NUM_SAMPLES \
      -tc '#000000,#FFFFFF' -obb 3 -ws -b 3 -id $TEMP_OUT_DIR -na 1 -f $HEIGHT -e png -wd $WIDTH \
      -m "$MARGIN,$MARGIN,$MARGIN,$MARGIN"
    cp $OUT_DIR/* $RESULT_DIR
  else
    cp $TEMP_OUT_DIR/* $RESULT_DIR
  fi
  rm -rf $OUT_DIR $TEMP_OUT_DIR
done
