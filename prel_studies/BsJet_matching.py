"""
    Study the matching efficiency between the Bs and Jet collection BEFORE any kinematic selection.
"""
from array import array
from PhysicsTools.NanoAODTools.postprocessing.tools import *
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Object, Event
from PhysicsTools.NanoAODTools.postprocessing.framework.treeReaderArrayTools import *
import ROOT
import math
#from officialStyle import officialStyle
from cmsstyle import CMS_lumi



ROOT.gROOT.SetBatch()   
ROOT.gStyle.SetOptStat(0)
#officialStyle(ROOT.gStyle, ROOT.TGaxis)


c1 = ROOT.TCanvas('c1', '', 700, 700)
c1.Draw()
c1.cd()
c1.SetTicks(True)

leg = ROOT.TLegend(0.24,.75,.95,.90)
leg.SetBorderSize(0)
leg.SetFillColor(0)
leg.SetFillStyle(0)
leg.SetTextFont(42)
leg.SetTextSize(0.035)

### some options
MAXFILES    = 5     # max files to process
MAXEVENTS   = -1    # max events to process
DEBUG       = False # helpful prints for debugging
PRINTEVERY  = int(1e4)  # print out the event number every N events

#samples = {"bstt":"/afs/cern.ch/user/f/friti/work/softtaus/CMSSW_13_0_10/src/bstt/reRunNano/crab_production/nanoaodv12_bstt.txt"}
# nanoAOD content to explore : https://cms-xpog.docs.cern.ch/autoDoc/
#samples = {"bstt":"./data/mcUL18_ParT_nanoAODv9.txt"}
samples = {"bstt":"./data/mcUL18_ParTedge_nanoAODv15.txt"}
decay = 'B_{s} #rightarrow  #tau #tau'

for sample in samples:
    files = open(samples[sample]).readlines()

    ####### histograms definition
    binw = 5 #GeV
    xlo,xhi = 0, 100
    nbins = int((xhi-xlo)/binw)
    den_histo = ROOT.TH1F("den","den",nbins,xlo,xhi)
    num_histo = ROOT.TH1F("num","num",nbins,xlo,xhi)

    den_histo.Sumw2()
    num_histo.Sumw2()
    ############# loop over the events
    if MAXFILES != -1: files = files[:MAXFILES]
    for fil in files:

        print("===> Processing file ",fil)
        fil = fil.strip("\n")
    
        infile = ROOT.TFile.Open(fil)        
        tree = InputTree(infile.Events)
        
        # loop over the entries
        nevents = tree.GetEntries() if MAXEVENTS == -1 else min(tree.GetEntries(), MAXEVENTS)
        for i in range(nevents):
            event = Event(tree,i)
            if (DEBUG) : print(f'## EVENT {i} ##')
            if i%PRINTEVERY == 0: print(f'processing {i}th event')

            genvistaus  = Collection(event, "GenVisTau") # hadronic taus
            jets        = Collection(event, "Jet")
            genparts    = Collection(event, "GenPart")
            jets_pt = [j.pt for j in jets]
            if min(jets_pt) < 10: continue # skip events with no jets

            # look for bs-> tau tau first
            for genpart in genparts:
                if abs(genpart.pdgId)!=531: continue #if not Bs continue
                daughters = []
                if (DEBUG): print(f" ({genpart._index}) Bs found pT = {genpart.pt} | pdgID {genpart.pdgId}")
                for g in genparts: # select taus coming from the Bs
                    if abs(g.pdgId)==15 and g.genPartIdxMother == genpart._index:
                        daughters.append(g)
                        if (DEBUG): print(f"\t ({g._index}) tau-daughter pT = {g.pt} | pdgID {g.pdgId}")

                if len(daughters) !=2: continue # Bs -> tau_x tau_x    

                ## request at least 1 tau to decay hadronically
                flag = 0
                for daughter in daughters:
                    for genvistau in genvistaus:
                        if (DEBUG) : print(f"\t\t genvistau with pT {genvistau.pt} | decay-mode {genvistau.status} | mother index {genvistau.genPartIdxMother}")
                        if genvistau.genPartIdxMother == daughter._index: flag += 1

                if flag > 0 :
                    den_histo.Fill(genpart.pt)
                    jet, dr = closest(genpart,jets)
                    j_btag = jet.btagDeepFlavB if jet is not None else -1
                    if (DEBUG) : print(f"\t\t closest jet with pT {jet.pt} | dR {dr:.3f} | btag {j_btag:.3f}")
                    if dr<0.4:
                        #print("dentro")
                        num_histo.Fill(genpart.pt)

            if (DEBUG) : print('#-------------------------------#')
                        
                
                
    ############ PLOTTING #########
    num_histo.Sumw2()
    den_histo.Sumw2()
    num_histo.Divide(den_histo)
    
    ## legend
    leg = ROOT.TLegend(0.24,.75,.95,.90)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)

    leg.AddEntry(num_histo,'B_{s}#rightarrow #tau_{h}#tau_{X};#Delta R <0.4','P')
    c1.cd()
    num_histo.SetTitle(";GEN B_{s} p_{T} (GeV) ;ak4/B_{s} matching efficiency")
    num_histo.SetFillColor(ROOT.kWhite)
    num_histo.SetLineColor(ROOT.kMagenta)
    num_histo.SetMarkerColor(ROOT.kMagenta)
    num_histo.SetMinimum(0)
    num_histo.SetMaximum(1.3)
    
    num_histo.Draw("EP2")
    num_histo.Draw("hist same")
    
    leg.Draw("same")
    #CMS_lumi(c1, 4, 0, cmsText = 'CMS', extraText = ' Simulation', lumi_13TeV = '')

    c1.SaveAs("efficiency_plot_new.png")
    
