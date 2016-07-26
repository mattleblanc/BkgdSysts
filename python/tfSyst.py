import os
import logging
import json
import math
import re
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

def get_scaleFactor(did, weights):
  scaleFactor = 1.0
  cutflow = weights[did[:6]].get('numevents')
  if cutflow == 0:
    raise ValueError('Num events = 0!')
  scaleFactor /= cutflow
  scaleFactor *= weights[did[:6]].get('cross section')
  scaleFactor *= weights[did[:6]].get('filter efficiency')
  scaleFactor *= weights[did[:6]].get('k-factor')
  return scaleFactor

def apply_sos_weight(did):
# sc_6c_1k_radHi = 2.06406 sc_1k_1k5_radHi = 2.17811 sc_1k5_radHi = 2.51412
# sc_6c_1k_radLo = 1.89614 sc_1k_1k5_radLo = 1.58018 sc_1k5_radLo = 1.52705
# sc_6c_1k_PowHPP = 2.00657 sc_1k_1k5_PowHPP = 2.14921 sc_1k5_radHi = 2.31007
    weight = 1.0
    if did=='407009' : weight = 1.00000
    if did=='407010' : weight = 1.00000
    if did=='407011' : weight = 1.00000
    if did=='407030' : weight = 2.06406
    if did=='407031' : weight = 2.17811
    if did=='407032' : weight = 2.51412
    if did=='407034' : weight = 1.89614
    if did=='407035' : weight = 1.58018
    if did=='407036' : weight = 1.52705
    if did=='407037' : weight = 2.00657
    if did=='407038' : weight = 2.14921
    if did=='407039' : weight = 2.31007

    return weight

# Parse command-line arguments from the user ...
parser = OptionParser()
parser.add_option("--cutstrings", help="JSON file containing regions and cutstrings which define them.",
                  default="${ROOTCOREBIN}/../BkgdSysts/cutstrings/multib_ichep2k16_regions.json")
parser.add_option("--systs", help="JSON file which contains the systematics to compute.",
                  default="${ROOTCOREBIN}/../BkgdSysts/config/multib_ichep2k16_ttbar.json")
parser.add_option("--event_weights", help="String of weights to apply for each event", default="1.0")
parser.add_option("--lumi_weights", help="Luminosity weight JSON file", default="config/weights.json")
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
            if options.verbose : logging.info("BkgdSyst\tfname is \t%s\t for did\t%s",fname,did)
            files[did]=ROOT.TFile.Open(fname)
            trees[did]=files[did].Get('nominal')
        
for did in trees:
    if options.verbose : logging.info("Tree for DID\t%s\thas\t%s\tentries.",did,trees[did].GetEntries())

# Loop over the different regions.
lumiweights = json.load(open(options.lumi_weights))
outfile = ROOT.TFile(options.output+options.systfile,"recreate")

sr_systs = {}
reg_yields = {}
for (syst,sets) in systematics.items():
    logging.info("syst\t%s",syst)
    hist = ROOT.TH1F(syst,syst,21,0.0,21)
    raw = ROOT.TH1F(syst+"_raw",syst+"_raw",56,0.0,56)

    for region in sorted(cutstrings):
        logging.info("region\t\t%s",region)

        tfs = {}
        for (scheme,samples) in sorted(sets.items()):
            yields = {}
            for (subreg,cuts) in sorted(cutstrings[region].items()):
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
                        
                if options.verbose : logging.info("Region Type\t\t\t%s",regtype)
                        
                # So, we want to know the yield for each of those regions, in each sample:
                nEvents=0.0
                for did in trees:
                    lumi = get_scaleFactor(did,lumiweights)
                    if(did in samples):
                        nEvents += apply_selection(trees[did],cuts,options.event_weights)*lumi*apply_sos_weight(did[:6])
                        raw.Fill(region+"_"+regtype+"_"+did, apply_selection(trees[did],cuts,'1.0'))
                        #logging.info("nEvents\t%s\traw\t%s",nEvents,apply_selection(trees[did],cuts,'1.0'))
                        yields[regtype] = nEvents
                        #if(scheme=='nominal') reg_yields[syst,region]=nEvents
                        
                if options.verbose : logging.info("DID\t\t\t\t\t%s\t%s",scheme,nEvents)
                if(scheme=='nominal' and regtype=='SR'): reg_yields[syst,region] = nEvents

            for (reg,nEvents) in yields.items():
                if(reg == "CR"): continue
                tfs[scheme+"_"+region+"_"+reg] = yields[reg]/yields["CR"]

        iBin=0
        for (reg,nEvents) in sorted(yields.items()):
            if(reg=="CR"): continue
            if "varied_"+region+"_"+reg in tfs:
                if tfs["nominal_"+region+"_"+reg] !=0 :
                    hist.Fill(region+"_"+reg,fabs(((tfs["nominal_"+region+"_"+reg]-tfs["varied_"+region+"_"+reg])/tfs["nominal_"+region+"_"+reg])*100.0))
                    if reg=="SR":
                        sr_systs[syst,region+"_"+reg]=fabs(((tfs["nominal_"+region+"_"+reg]-tfs["varied_"+region+"_"+reg])/tfs["nominal_"+region+"_"+reg]))
            elif "varyUp_"+region+"_"+reg and "varyDown_"+region+"_"+reg in tfs:   
                if (fabs(tfs["varyUp_"+region+"_"+reg])+fabs(tfs["varyDown_"+region+"_"+reg])) !=0:
                    hist.Fill(region+"_"+reg,2.0*fabs(tfs["varyUp_"+region+"_"+reg]-tfs["varyDown_"+region+"_"+reg])/fabs(tfs["varyUp_"+region+"_"+reg]+tfs["varyDown_"+region+"_"+reg])*100.0)
                    if reg=="SR":
                        sr_systs[syst,region+"_"+reg]=2.0*fabs(tfs["varyUp_"+region+"_"+reg]-tfs["varyDown_"+region+"_"+reg])/fabs(tfs["varyUp_"+region+"_"+reg]+tfs["varyDown_"+region+"_"+reg])

    hist.SetStats(0)
    hist.GetXaxis().SetTitle("Region")
    hist.GetXaxis().SetTitleOffset(1.33)
    hist.GetYaxis().SetTitleOffset(1.33)
    hist.GetYaxis().SetTitle("Percent Uncertainty")
    hist.SetMarkerStyle(5)
    hist.SetMarkerSize(1)

    canvas = ROOT.TCanvas('draw', 'draw', 0, 0, 1400, 1050)
    pad = ROOT.TPad()
    canvas.cd()
    hist.Draw("hist P")
    if options.atlas :
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
    canvas.SaveAs(options.output+syst+".pdf")
    canvas.SaveAs(options.output+syst+".root")

    canvas.Clear()
    raw.SetStats(0)
    raw.GetXaxis().SetTitle("Region")
    raw.GetXaxis().SetTitleOffset(1.33)
    raw.GetYaxis().SetTitleOffset(1.33)
    raw.GetYaxis().SetTitle("Raw Yield")
    raw.Draw("hbar")
    if options.atlas :
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
    canvas.SaveAs(options.output+syst+"_raw_yields.pdf")
    canvas.SaveAs(options.output+syst+"_raw_yields.root")

#outfile.Write()
#outfile.Close()

total_syst = ROOT.TH1F('total','total',21,0.0,21)
total_syst_bb = ROOT.TH1F('total_bb','total_bb',21,0.0,21)
total_syst_cc = ROOT.TH1F('total_cc','total_cc',21,0.0,21)
total_syst_ll = ROOT.TH1F('total_ll','total_ll',21,0.0,21)

#total_yield = ROOT.TH1F('yield','yield',21,0.0,21)
total_yield_bb = ROOT.TH1F('yield_bb','yield_bb',21,0.0,21)
total_yield_cc = ROOT.TH1F('yield_cc','yield_cc',21,0.0,21)
total_yield_ll = ROOT.TH1F('yield_ll','yield_ll',21,0.0,21)

print "reg yields",reg_yields

for syst,reg in sr_systs:
    
    print reg
    if(string.find(reg,'ttbb')>=0): total_syst_bb.Fill(reg[:-5],sr_systs[syst,reg]*sr_systs[syst,reg])
    if(string.find(reg,'ttcc')>=0): total_syst_cc.Fill(reg[:-5],sr_systs[syst,reg]*sr_systs[syst,reg])
    if(string.find(reg,'ttll')>=0): total_syst_ll.Fill(reg[:-5],sr_systs[syst,reg]*sr_systs[syst,reg])
    #total_syst.Fill(reg,sr_systs[syst,reg]*sr_systs[syst,reg])

    print reg,reg_yields[syst,reg[:-3]]

    if(string.find(reg,'ttbb')>=0): total_yield_bb.Fill(reg[:-8],reg_yields[syst,reg[:-3]])
    if(string.find(reg,'ttcc')>=0): total_yield_cc.Fill(reg[:-8],reg_yields[syst,reg[:-3]])
    if(string.find(reg,'ttll')>=0): total_yield_ll.Fill(reg[:-8],reg_yields[syst,reg[:-3]])

#reg_fracs[syst,reg[:-6],reg[-5:]]=reg_yields[syst,reg]/
    
for bin in range(1,total_syst_bb.GetNbinsX() + 1):
    total_yield = total_yield_bb.GetBinContent(bin)+total_yield_cc.GetBinContent(bin)+total_yield_ll.GetBinContent(bin)
    print total_yield
    print total_yield_bb.GetBinContent(bin),total_yield_cc.GetBinContent(bin),total_yield_ll.GetBinContent(bin)
    if total_yield != 0:
        frac_bb = total_yield_bb.GetBinContent(bin)/total_yield
        frac_cc = total_yield_cc.GetBinContent(bin)/total_yield
        frac_ll = total_yield_ll.GetBinContent(bin)/total_yield
        print frac_bb,frac_cc,frac_ll
        total_syst.SetBinContent(bin,math.sqrt(total_syst_bb.GetBinContent(bin)*total_syst_bb.GetBinContent(bin)*(frac_bb)+total_syst_cc.GetBinContent(bin)*total_syst_cc.GetBinContent(bin)*(frac_cc)+total_syst_ll.GetBinContent(bin)*total_syst_ll.GetBinContent(bin)*(frac_ll)))
        total_syst.GetXaxis().SetBinLabel(bin,total_yield_cc.GetXaxis().GetBinLabel(bin))

#total_syst.Print()

total_syst.Draw("hist")
total_syst.Write();
canvas.SaveAs(options.output+"total_syst.pdf")
canvas.SaveAs(options.output+"total_syst.root")

outfile.Write()
outfile.Close()
