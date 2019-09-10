#!/bin/bash

# Parses without saving any gt recs
#python3 parse_cornell.py ~/DATASETS/cornell_dataset/

# If visualization, positive gt recs only
#python3 parse_cornell.py ~/DATASETS/cornell_dataset/ ~/DATASETS/cornell_dataset/vis_recs

# If visualization, positive and negative gt recs
python3 parse_cornell.py ~/DATASETS/cornell_dataset/ ~/DATASETS/cornell_dataset/vis_recs negs