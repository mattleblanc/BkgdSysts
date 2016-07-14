import os
import logging
import json
import string
import glob
import ROOT
from ROOT import gROOT,gPad,gStyle,TCanvas,TFile,TLine,TLatex,TAxis,TLegend,TPostScript
from optparse import OptionParser
from math import fabs

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptTitle(False)
logging.basicConfig(level=logging.INFO)
logging.info("Calculating transfer factor systematics . . .")

global canvas

def apply_selection(tree, cuts, eventWeightBranch):
    canvas = ROOT.TCanvas('test', 'test', 200, 10, 100, 100)
    tree.Draw(eventWeightBranch, '{0:s}*{1:s}'.format(cuts,eventWeightBranch))
    weightedCount = 0
    # get drawn histogram
    if 'htemp' in canvas:
      htemp = canvas.GetPrimitive('htemp')
      weightedCount = htemp.Integral()
    canvas.Clear()
    return weightedCount

# Parse command-line arguments from the user ...
parser = OptionParser()
parser.add_option("--cutstrings", help="JSON file containing regions and cutstrings which define them.",
                  default="${ROOTCOREBIN}/../BkgdSysts/cutstrings/multib_ichep2k16_regions.json")
parser.add_option("--systs", help="JSON file which contains the systematics to compute.",
                  default="${ROOTCOREBIN}/../BkgdSysts/config/multib_ichep2k16_ttbar.json")
parser.add_option("--weights", help="String of weights to apply for each event", default="1.0")
parser.add_option("--input", help="Directory of input ROOT files", default="${ROOTCOREBIN}/../BkgdSysts/input/")
parser.add_option("--output", help="Directory of output files", default="${ROOTCOREBIN}/../BkgdSysts/output/")
parser.add_option("--systfile", help="Name of output .root file with systematics", default="bkgsyst.root")
parser.add_option("--atlas", action='store_true', help="Add ATLAS labels to output plots?", dest="atlas")
parser.add_option("--verbose", action='store_true', help="Verbose output?", dest="verbose")

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
trees = {}
for fname in glob.glob(options.input):
    for did in dids:
        if(string.find(fname,did)>=0):
            logging.info("BkgdSyst\tfname is \t%s\t for did\t%s",fname,did)
            files[did]=ROOT.TFile.Open(fname)
            trees[did]=files[did].Get('nominal')
        
for did in trees:
    if(options.verbose): logging.info("Tree for DID\t%s\thas\t%s\tentries.",did,trees[did].GetEntries())

# Loop over the different regions.

outfile = ROOT.TFile(options.output+options.systfile,"recreate")

for (syst,sets) in systematics.items():
    logging.info("syst\t%s",syst)
    hist = ROOT.TH1F(syst,syst,21,0.0,21)

    for region in cutstrings:
        logging.info("region\t\t%s",region)

        tfs = {}
        for (scheme,samples) in sets.items():
            yields = {}
            for (subreg,cuts) in cutstrings[region].items():
                regtype="NULL"
                # string.find returns -1 if not match, or the index of the position of the match if there is one:
                # 0 means the string starts with the match!
                
                if string.find(subreg,"SR")>=0 :
                    regtype="SR"
                if string.find(subreg,"CR")>=0 :
                    regtype="CR"
                if string.find(subreg,"VR1")>=0 :
                    regtype="VR1"
                if string.find(subreg,"VR2")>=0 :
                    regtype="VR2"
                        
                if(options.verbose): logging.info("Region Type\t\t\t%s",regtype)
                        
                # So, we want to know the yield for each of those regions, in each sample:
                nEvents=0.0
                for did in trees:
                    if(did in samples):
                        #nEvents += trees[did].GetEntries(cuts+options.weights)
                        #print apply_selection(trees[did],cuts,options.weights)
                        nEvents += apply_selection(trees[did],cuts,options.weights)
                        yields[regtype] = nEvents
                        
                if(options.verbose): logging.info("DID\t\t\t\t\t%s\t%s",scheme,nEvents)

            for (reg,nEvents) in yields.items():
                if(reg == "CR"): continue
                tfs[scheme+"_"+region+"_"+reg] = yields[reg]/yields["CR"]

        iBin=0
        for (reg,nEvents) in yields.items():
            if(reg=="CR"): continue
            if "varied_"+region+"_"+reg in tfs:
                hist.Fill(region+"_"+reg,fabs(((tfs["nominal_"+region+"_"+reg]-tfs["varied_"+region+"_"+reg])/tfs["nominal_"+region+"_"+reg])*100.0))
            elif "varyUp_"+region+"_"+reg and "varyDown_"+region+"_"+reg in tfs:   
                hist.Fill(region+"_"+reg,fabs(tfs["varyUp"]/tfs["varyDown"])*100.0)

    hist.SetStats(0)
    hist.GetXaxis().SetTitle("Region")
    hist.GetXaxis().SetTitleOffset(1.33)
    hist.GetYaxis().SetTitleOffset(1.33)
    hist.GetYaxis().SetTitle("Percent Uncertainty")
    hist.SetMarkerStyle(5)
    hist.SetMarkerSize(1)

    canvas = ROOT.TCanvas('draw', 'draw', 0, 0, 800, 600)
    pad = ROOT.TPad()
    canvas.cd()
    hist.Draw("hist P")
    if(options.atlas):
        l=TLatex()
        l.SetNDC()
        l.SetTextFont(72)
        l.DrawLatex(0.15,0.85,"ATLAS")
        p=TLatex()
        p.SetNDC();
        p.SetTextFont(42)
        p.DrawLatex(0.28,0.85,"Internal");
        q=TLatex()
        q.SetNDC();
        p.SetTextFont(41)
        q.DrawLatex(0.15,0.80,syst);

    hist.Write();
    canvas.SaveAs("output/"+syst+".pdf")

outfile.Write()
outfile.Close()
