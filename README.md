# BkgdSysts

This is a small utility which will hopefully make computing "theoretical" systematic uncertainties on various background processes a little bit easier. For example, this kind of comparison is pretty commonly done withing the [ATLAS experiment](http://atlas.web.cern.ch/Atlas/Collaboration/) SUSY working group.

To check the package out, do

```
git clone ssh://git@gitlab.cern.ch:7999/MultiBJets/BkgdSysts.git
```

To run, you'll want to point `tfSyst.py` at the necessary config files like in the following example:

```
	python python/tfSyst.py \
		--cutstrings cutstrings/multib_ichep2k16_regions.json \
		--systs config/multib_ichep2k16_ttbar.json \
		--weights 'weight_mc*weight_jvt*weight_pu*weight_muon*weight_elec*weight_btag' \
		--input 'input/*.root' \
		--output 'output/' \
		--systfile 'bkgsyst_test.root' \
		--verbose
```

# Links

[University of Victoria VISPA](https://www.uvic.ca/science/physics/vispa/)

[Natural Sciences and Engineering Research Council of Canada](http://www.nserc-crsng.gc.ca/)

[ATLAS Experiment](http://atlas.cern) at [CERN](http://home.cern)

[arXiv:1605.09318](http://arxiv.org/abs/1605.09318)
