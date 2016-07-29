#!/bin/bash

python python/yieldSyst.py \
    --cutstrings cutstrings/multib_ichep2k16_regions.json \
    --systs config/multib_ichep2k16_singletop_ISRFSR.json \
    --lumi_weights 'config/theory_weights.json' \
    --event_weights 'weight_mc*weight_jvt*weight_muon*weight_elec*weight_btag' \
    --input '/faxbox2/user/mleblanc/multib_ichep2k16/theory/theorysingletop.*.root' \
    --output 'output_singletop/' \
    --systfile 'bkgsyst_multib_singletop.root' \
    --atlas \
    --verbose