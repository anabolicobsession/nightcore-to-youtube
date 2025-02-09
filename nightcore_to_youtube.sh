#!/bin/bash

project_dir=$(dirname $(realpath "$0"))

# set up PYTHONPATH to be able run script from anywhere
export PYTHONPATH="$project_dir"

# set up correct conda environment
source "$HOME/apps/miniconda3/etc/profile.d/conda.sh"
conda activate nightcore_to_youtube

python "$project_dir/src/main.py" "$@"
