#!/bin/bash
# this script copies the folder structure and json/cfg files from a grid search working directory to the target directory
# this should be executed in the working directory folder 
target_path="/home/groot/mmDetection/grid_search_lr_mom/copy_grid_folders_json_config.sh"

find . -name '*.json' -exec cp --parents \{\} /$target_path \;
find . -name '*.py' -exec cp --parents \{\} /$target_path \;
