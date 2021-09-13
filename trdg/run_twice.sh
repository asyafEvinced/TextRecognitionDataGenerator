#!/bin/bash
RESULT_DIR='res'
if [ ! -d $RESULT_DIR ];
then
  mkdir $RESULT_DIR
fi
OUT_DIR='out'
TEMP_OUT_DIR='out_1'
for i in {1..3}
do
  if [ ! -d $OUT_DIR ];
  then
    mkdir $OUT_DIR
  fi
  if [ ! -d $TEMP_OUT_DIR ];
  then
    mkdir $TEMP_OUT_DIR
  fi
  WIDTH=$((100 + $RANDOM % 800))
  HEIGHT=$((64 + $RANDOM % 100))
  NUM_WORDS_BACKGROUND=$((1 + $RANDOM % 5))
  NUM_WORDS_FOREGROUND=$((1 + $RANDOM % 5))
  python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c 3 -w $NUM_WORDS_BACKGROUND \
    -tc '#000000,#FFFFFF' -obb 1 -ws -b 4 -na 1 -wd $WIDTH -f $HEIGHT --output_dir $TEMP_OUT_DIR
  python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c 3 -w $NUM_WORDS_FOREGROUND \
    -tc '#000000,#FFFFFF' -obb 1 -ws -b 3 -id $TEMP_OUT_DIR -na 1 -f $HEIGHT
  cp $OUT_DIR/* $RESULT_DIR
  rm -rf $OUT_DIR $TEMP_OUT_DIR
done
