#!/bin/bash


# check for required arguments
if [[ $# -lt 2 || $# -gt 3 ]]; then
  echo "Usage: $0 <mp3> <image> [preset]"
  exit 1
fi

mp3="$1"
image="$2"
preset=${3:-medium}

mp3_basename=$(basename "$mp3")
output="${mp3_basename%.mp3}.mp4"


# get image dimensions
read width height < <(identify -format "%w %h" "$image")

if (( height >= 1080 )); then
  # image height is greater than 1080p, output 1920x1080
  ffmpeg -loop 1 -i "$image" -i "$mp3" -c:v libx264 -crf 18 -preset "$preset" -c:a copy -shortest -vf "scale=1920:1080" "$output"

else
  # scale image to fit 1080p height while maintaining aspect ratio
  new_width=$(( (height * 16) / 9 ))
  pad_left=$(( (new_width - width) / 2 ))
  ffmpeg -y -loop 1 -i "$image" -i "$mp3" -c:v libx264 -crf 18 -preset "$preset" -c:a copy -shortest -vf "pad=width=$new_width:height=$height:x=$pad_left:y=0:color=black" "$output"
fi

if [[ $? -eq 0 ]]; then
  echo "Processed: $mp3 -> ${mp3%.mp3}.mp4"
else
  echo "Error processing: $mp3" >&2
fi
