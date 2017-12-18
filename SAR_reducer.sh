#!/bin/bash
#
# This script creates the final output.
#
# - Data location: /root/SAR_app/deployment/reducer/
# - Output: animated GIF
#
set -e
set -x
source ~/SAR_app/deployment/lib.sh

echo "@REDUCER_RUN - "$(timestamp)" - start processing"
output=SAR_animation_$(date +%s).gif
base_path=~/SAR_app/deployment/reducer
convert -delay 90 -loop 0 $base_path/*.png $base_path/$output
echo "@REDUCER_RUN - "$(timestamp)" - finish processing"
#get_file_size $output"
