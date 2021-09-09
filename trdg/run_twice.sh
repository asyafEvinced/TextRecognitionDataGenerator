#!/bin/bash
WIDTH=$((100 + $RANDOM % 1000))
HEIGHT=64
python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c 3 -w 3 -tc '#000000,#FFFFFF' \
  -obb 1 -ws -b 1 -na 1 -wd $WIDTH -f $HEIGHT
mv out out_1
python /Users/asya/Code/TextRecognitionDataGenerator/trdg/run.py -c 3 -w 1 -tc '#000000,#FFFFFF' \
  -obb 1 -ws -b 3 -id ./out_1 -na 1 -f $HEIGHT
mv out out_2
