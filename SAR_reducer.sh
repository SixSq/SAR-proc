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

echo "@REDUCER_RUN - "$(date +%s)" - start processing"
output=SAR_animation_$(date +%s).gif
base_path=${PROCESSED_DATA_LOC:-.}
convert -delay 90 -loop 0 $base_path/*.png $base_path/$output
echo "@REDUCER_RUN - "$(date +%s)" - finish processing"
#get_file_size $output"
