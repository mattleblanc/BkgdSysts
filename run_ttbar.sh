#!/bin/bash

python python/tfSyst.py \
    --cutstrings cutstrings/multib_ichep2k16_regions_splitflav.json \
    --systs config/multib_ichep2k16_ttbar.json \
    --lumi_weights 'config/weights.json' \
    --event_weights 'weight_mc*weight_jvt*weight_muon*weight_elec*weight_btag*weight_WZ_2_2' \
    --input '/global/mleblanc/multib_ichep16/bgsyst/merge/*.root' \
    --output 'output_ttbar/' \
    --systfile 'bkgsyst_multib_ttbar.root' \
    --atlas \
    --splitFlavour \
    --verbose
