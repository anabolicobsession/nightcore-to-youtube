#!/bin/bash

source "$HOME/apps/miniconda3/etc/profile.d/conda.sh"
conda activate nightcore_to_youtube
python main.py "$@"
