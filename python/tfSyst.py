import os
import logging
import json
from optparse import OptionParser

logging.basicConfig(level=logging.INFO)

logging.info("Calculating transfer factor systematics . . .")

# Parse command-line arguments from the user ...
parser = OptionParser()
parser.add_option("--cutstrings", help="JSON file containing regions and cutstrings which define them.",
                  default="${ROOTCOREBIN}/../BkgdSysts/cutstrings/multib_ichep2k16.json")

(options, args) = parser.parse_args()

cutstrings = json.load(open(options.cutstrings));

logging.info("\tFound %d region definitions.",len(cutstrings))

# Loop over the different regions.
for region in cutstrings:

    logging.info("BkgdSyst\tregion\t%s",region)


