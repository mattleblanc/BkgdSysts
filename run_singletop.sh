#!/bin/bash

python python/yieldSyst.py \
    --cutstrings cutstrings/multib_ichep2k16_regions_2b.json \
    --systs config/multib_ichep2k16_singletop.json \
    --lumi_weights 'config/weights.json' \
    --event_weights 'weight_mc*weight_jvt*weight_muon*weight_elec*weight_btag' \
    --input '/global/mleblanc/multib_ichep16/bgsyst/merge/*.root' \
    --output 'output_singletop/' \
    --systfile 'bkgsyst_multib_singletop.root' \
    --atlas \
    --verbose