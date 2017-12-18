# Sentinel 1 (SAR) app processing module

This repository is an example of processing module for [SAR-app](https://github.com/SixSq/SAR-app/) by SixSq. 
Its purpose is to provide the possibility to process SAR data with your own `mapper` and `reducer` functions.

## Instructions

1. Fork this repository
    ```
    $ git clone https://github.com/YOUR_USERNAME/SAR-app.git
     ```
1. Do not change the file stucture (i.e. `SAR_mapper.py` and `SAR_reducer.sh` should stay at the root.)

1. Implement your own mapper and reducer.

1. The repository's name must stay as `SAR_proc`

*Note: data files are located in the root directory of the mapper and reducer scripts by default.*
