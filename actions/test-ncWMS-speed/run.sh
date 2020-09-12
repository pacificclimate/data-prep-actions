#!/bin/bash
python test-ncWMS-speed.py \
  --ncwms=https://services.pacificclimate.org/pcex/ncwms \
  --dataset=tasmean_aClimMean_anusplin_historical_19610101-19901231 \
  --delay=2.0 \
  --interval=0.01 \
  --count=10 -y
