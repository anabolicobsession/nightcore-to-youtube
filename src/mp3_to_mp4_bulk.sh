#!/bin/bash


# check for required arguments
if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 <directory> [preset]"
  exit 1
fi

dir="$1"
preset="$2"
image=$(find "$dir" -maxdepth 1 -name "*.png" -print -quit)
script="$HOME/code/nightcore_to_youtube/mp3_to_mp4.sh"


find "$dir" -maxdepth 1 -type f -regex '.*[0-9_]\.mp3$' -print0 | xargs -0 -P 4 -I {} bash -c ''$script' "{}" '$image' '$preset''
