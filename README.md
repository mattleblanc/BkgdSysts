# BkgdSyst

We're going to calculate your background systematics, and we're going to do a fine job of it.

To check the package out, do

```
rcSetup Base,2.4.11
git clone ssh://git@gitlab.cern.ch:7999/MultiBJets/BkgdSysts.git
```

To run, you'll want to point `tfSyst.py` at the necessary config files like in the following example:

```
	python python/tfSyst.py \
		--cutstrings cutstrings/multib_ichep2k16_regions.json \
		--systs config/multib_ichep2k16_ttbar.json \
		--input 'input/*.root' \
		--output 'output/' \
		--systfile 'bkgsyst_test.root' \
		--verbose
```
