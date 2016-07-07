# BkgdSyst

We're going to calculate your background systematics, and we're going to do a fine job of it.

To check the package out, do

```
rcSetup Base,2.4.11
git clone ssh://git@gitlab.cern.ch:7999/MultiBJets/BkgdSysts.git
```

To run, you'll want to point `tfSyst.py` at the necessary config files like in the following example:

```
python BkgdSysts/python/tfSyst.py \
       --cutstrings BkgdSysts/cutstrings/multib_ichep2k16_regions.json \
       --systs BkgdSysts/config/multib_ichep2k16_ttbar.json \
       --input '/faxbox2/user/user/mleblanc/multib_ichep2k16/hf_tag2.4.11-1-0/optin/*.root'
```