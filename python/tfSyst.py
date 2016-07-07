import os
import logging
import json
import string
import glob
import ROOT
from optparse import OptionParser

logging.basicConfig(level=logging.INFO)

logging.info("Calculating transfer factor systematics . . .")

# Parse command-line arguments from the user ...
parser = OptionParser()
parser.add_option("--cutstrings", help="JSON file containing regions and cutstrings which define them.",
                  default="${ROOTCOREBIN}/../BkgdSysts/cutstrings/multib_ichep2k16_regions.json")
parser.add_option("--systs", help="JSON file which contains the systematics to compute.",
                  default="${ROOTCOREBIN}/../BkgdSysts/config/multib_ichep2k16_ttbar.json")
parser.add_option("--input", help="Directory of input ROOT files", default="${ROOTCOREBIN}/../BkgdSysts/input/")

(options, args) = parser.parse_args()

cutstrings = json.load(open(options.cutstrings));
systematics = json.load(open(options.systs));

logging.info("Found %d region definitions.",len(cutstrings))

# Open all the files ...

dids = []
for syst in systematics:
    # Open all the files we need ...
    for state in systematics[syst]:
        for did in systematics[syst][state]:
            if did not in dids:
                dids.append(did)

files = {}
for fname in glob.glob(options.input):
    for did in dids:
        if(string.find(fname,did)>=0):
            logging.info("BkgdSyst\tfname is \t%s\t for did\t%s",fname,did)
            files[did]=fname

# Loop over the different regions.
for syst in systematics:
    logging.info("BkgdSyst\tsyst\t%s",syst)
    for variation in systematics[syst]:
        logging.info("BkgdSyst\tvariation\t%s",variation) 
        for region in cutstrings:
            logging.info("BkgdSyst\t\tregion\t%s",region)
            for subreg in cutstrings[region]:
                regtype="NULL"
                # string.find returns -1 if not match, or the index of the position of the match if there is one:
                # 0 means the string starts with the match!
                if string.find(subreg,"SR")>=0 :
                    regtype="SR"
                if string.find(subreg,"CR")>=0 :
                    regtype="CR"
                if string.find(subreg,"VR")>=0 :
                    regtype="VR"
                logging.info("BkgdSyst\t\t\tsubreg\t%s",regtype)
