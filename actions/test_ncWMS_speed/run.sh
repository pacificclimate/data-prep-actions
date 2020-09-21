#!/bin/bash
python test-ncWMS-speed-async.py --file=spec1.yaml
#python test-ncWMS-speed-async.py \
#  --ncwms=https://services.pacificclimate.org/dev/pcex/ncwms \
#  --dataset=x/storage/data/climate/downscale/BCCAQ2/ANUSPLIN/climatologies/prsn_aClimMean_anusplin_historical_19610101-19901231.nc/prsn \
#  --request=GetMap \
#  --time=1977-07-01T00:00:00Z \
#  --delay=0 \
#  --interval=1 \
#  --count=2 -y
#python test-ncWMS-speed-async.py \
#  --ncwms=https://services.pacificclimate.org/dev/pcex/ncwms \
#  --dataset=x/storage/data/projects/comp_support/climate_explorer_data_prep/climatological_means/plan2adapt/pcic12/prsn_aClimMean_BCCAQv2_PCIC12_historical+rcp85_rXi1p1_20400101-20691231_Canada.nc/prsn \
#  --request=GetMap \
#  --time=2055-07-02T00:00:00Z \
#  --delay=2.0 \
#  --interval=0.0 \
#  --count=100
#python test-ncWMS-speed-async.py \
#  --ncwms=https://services.pacificclimate.org/dev/pcex/ncwms \
#  --dataset=x/storage/data/projects/comp_support/climate_explorer_data_prep/climatological_means/plan2adapt/pcic12/prsn_aClimMean_BCCAQv2_PCIC12_historical+rcp85_rXi1p1_20400101-20691231_Canada.nc/prsn \
#  --request=GetMap \
#  --time=2055-07-02T00:00:00Z \
#  --delay=2.0 \
#  --interval=0.0 \
#  --count=10
#python test-ncWMS-speed-async.py \
#  --ncwms=https://services.pacificclimate.org/dev/pcex/ncwms \
#  --dataset=x/storage/data/climate/downscale/BCCAQ2/ANUSPLIN/climatologies/cdd_aClimMean_anusplin_historical_19610101-19901231.nc/cdd \
#  --request=GetMap \
#  --time=1977-07-02T00:00:00Z \
#  --delay=2.0 \
#  --interval=1 \
#  --count=2
#python test-ncWMS-speed-async.py \
#  --ncwms=https://services.pacificclimate.org/dev/pcex/ncwms \
#  --dataset=x/storage/data/projects/comp_support/climate_explorer_data_prep/climatological_means/plan2adapt/pcic12/tasmean_mClimMean_BCCAQv2_PCIC12_historical+rcp85_rXi1p1_20700101-20991231_Canada.nc/tasmean \
#  --request=GetMap \
#  --time=2085-07-02T00:00:00Z \
#  --delay=2.0 \
#  --interval=1 \
#  --count=2
#python test-ncWMS-speed-async.py \
#  --ncwms=https://services.pacificclimate.org/pcex/ncwms \
#  --dataset=tasmean_aClimMean_anusplin_historical_19610101-19901231 \
#  --delay=2.0 \
#  --interval=0.01 \
#  --count=10
#python test-ncWMS-speed.py \
#  --ncwms=https://services.pacificclimate.org/pcex/ncwms \
#  --dataset=tasmean_aClimMean_anusplin_historical_19610101-19901231 \
#  --delay=2.0 \
#  --interval=0.01 \
#  --count=10 -y
