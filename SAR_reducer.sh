#!/bin/bash
#
# This script creates the final result by reducing the processed
# image set in to an animation.
#
# - Input: data location as $PROCESSED_DATA_LOC environment variable
# - Output: animated GIF
#
set -e
set -x

echo "@REDUCER_RUN $(date +%s) start reducing"
input_path=${1:-.}
output=${2:-.}/SAR_animation_$(date +%s).gif
convert -delay 90 -loop 0 $input_path/*.png $output
echo "@REDUCER_RUN $(date +%s) finish reducing"
