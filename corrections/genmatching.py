'''
    Study the efficiency in matching Bs with b-tag jets @ gen-level
    - CHS jets
    - PUPPI jets
'''

import os, sys
import argparse
import uproot
import awkward as ak
import numpy as np

import ROOT
ROOT.gROOT.SetBatch()   
ROOT.gStyle.SetOptStat(0)

# --- plotting libraries ---
import matplotlib.pyplot as plt
#import mplhep as hep
#plt.style.use([hep.style.ROOT, hep.style.firamath])

# custom import
import data_toolkit as data
import utils.logger as logger
import utils as utils

def parse_arguments():
    parser = argparse.ArgumentParser(description="Apply corrections to ntuples")
    parser.add_argument("--input", "-i", 
                        required=True, 
                        help=".yml file containing the input ntuples locations and metadata"
                        )
    parser.add_argument("--outdirectory", "-o",
                        default=None,
                        help="Directory to save output ntuples (created if does not exist). Overwrites the location in the input .yml file if provided.",
                        )
    parser.add_argument('--channels', 
                        nargs='+', 
                        default=['emu'],
                        help='Select channels to process')
    parser.add_argument("--nevents", "-N",
                        type=int,
                        default=-1,
                        help="Number of events to process (default: -1 = all events)",
                        )
    parser.add_argument("--tag",
                        default="CHSAK4",
                        help="Tag for the output files (default: v1)",
                        )
    parser.add_argument("--test", "-t",
                        action="store_true",
                        help="Run in test mode (process only a small subset of events)",
                        )
    return parser.parse_args()


if __name__ == "__main__":
    
    
    args = parse_arguments()
    
    if os.path.isfile(args.input): in_info = data.samples.parse_inyml(args.input)
    else : logger.print_error(f"Input file {args.input} does not exist."); sys.exit(1)
    
    channels    = [c.strip().strip(',') for c in args.channels]
    print(f"[INFO] Processing channels: {channels}")
    year        = str(in_info.get('common', {}).get('year', 2018))
    _testmode_  = args.test
    _nevents    = args.nevents if args.nevents > 0 else None
    tmp_outdir  = os.path.join(os.getcwd(), "tmp_output")
    tag         = args.tag

    # info from external .yml file
    tree_dir_base = in_info.get('MC', {}).get('inpath_template', None)
    out_dir_base  = args.outdirectory if args.outdirectory else in_info.get('MC', {}).get('outpath_template', None)
    _tree_name = in_info.get('common', {}).get('treename', 'Events')

    # get signal sample
    mc_samples_names = data.samples.mc_samples_names
    signal_sample = [s for s in mc_samples_names if 'bstautau' in s]

    for channel in channels:
        print(f"\n ----------- CHANNEL {channel} -----------")
        
        # I/O directories
        tree_dir = tree_dir_base.format(channel=channel)
        out_dir  = out_dir_base.format(channel=channel)
        if not os.path.exists(out_dir): os.makedirs(out_dir)
        logger.print_info(f"[I/O] Input: {tree_dir} | Output: {out_dir}")
        mc_samples = data.ioutils.load_mc_samples(
                tree_dir,
                signal_sample,
                year,
                data.samples.files_names,
                _tree_name,
                nevents = _nevents
            )

        for name, rdf in mc_samples.items():
            
            Ninit = rdf.Count().GetValue()

            # trigger selections (OR of the requirements in data)
            hlt_conditions = data.selection.trigger_selections.get(channel, {})
            hlt_paths      = [hlt_conditions.get(dset, "(1)") for dset in hlt_conditions]
            hlt_sel        = ' | '.join(hlt_paths)
            print(f" [SKIM] trigger selection: {hlt_sel}")

            mc_samples[name] = mc_samples[name].Filter(hlt_sel)

            # define invariant mass and transverse mass
            mc_samples[name] = data.defutils.define_invariant_mass_and_mt(mc_samples[name], channel)
            
            # define jets passing minimal kinematics and b-tagging conditions
            jet_sel          = data.selection.min_jet_selection.get(channel, "(1)")
            mc_samples[name] = data.defutils.define_jets_with_minimum_selection(
                mc_samples[name], 
                jet_sel
            )
            
            mc_samples[name] = data.defutils.define_jets_with_minimum_selection_for_histos(
                mc_samples[name], 
                is_bstautau=False, 
                bstautau_conditions=data.selection.bstautau_conditions
            )
            mc_samples[name] = data.defutils.define_jets_with_btagging_selection_for_filters(mc_samples[name])
            mc_samples[name] = data.defutils.define_btagging_conditions(mc_samples[name], channel) # FIXME : saves conditions for all channels | external dep form btagging cond.
            mc_samples[name] = data.defutils.define_jet_conditions(mc_samples[name], channel, jet_sel) # FIXME : saves conditions for all channels | external dep form jet cond.
            
            # preselections
            pre_sel = data.selection.preselection.get(channel, "(1)")
            print(f" [SKIM] preselection: {pre_sel}")
            mc_samples[name] = mc_samples[name].Filter(pre_sel)

            # jet conditions
            print(f" [SKIM] jet selection: {jet_sel}")
            mc_samples[name] = mc_samples[name].Filter(f"ROOT::VecOps::Any({jet_sel})")
            
            Nsel = mc_samples[name].Count().GetValue()
            logger.print_info(f"[{name}] events saved/read = {Nsel}/{Ninit} ({100*Nsel/Ninit:.2f}%)")

            # --- save temporary snapshot
            print(f"[I/O] Saving temporary snapshot to {tmp_outdir}")
            if not os.path.exists(tmp_outdir):
                os.makedirs(tmp_outdir)
            tmp_outpath = os.path.join(tmp_outdir, f"tmp_{data.samples.files_names[name]}.root")
            mc_samples[name].Snapshot(_tree_name, tmp_outpath)
            if os.path.isfile(tmp_outpath):
                print(f"[OUTPUT] Saved processed sample to {tmp_outpath}")
            else:
                print(f"[ERROR] Failed to save processed sample to {tmp_outpath}")
                sys.exit(1)

            # load snapshot back as an awkward array for downstream processing
            with uproot.open(tmp_outpath) as f:
                n_events_in = f[_tree_name].num_entries
                mcdf        = f[_tree_name].arrays(library="ak")
                print(f" + {n_events_in} events read from {tmp_outpath}")
            if n_events_in == 0:
                print(f"[{name}] 0 events survive selection — skipping SF step, writing empty tree")
                continue
            

            data.defutils.match_BsToJets(mcdf,
                                         sigflag= 'GenCand_isBsTauTau',
                                         jetcollection = 'j',    
                                         btag_wp= data.selection.btag_wpval['L'], 
                                         max_dr=0.4, min_jet_pt=20.0, max_jet_eta=2.5,
                                         debug=_testmode_
                                        )

            # plot gen matching efficiency
            # ---------- select signal Bs per event ----------
            bs_pt       = mcdf['GenCand_pt'][mcdf['GenCand_isBsTauTaunew'] == 1]     # [n_events, n_bs]

            
            has_match   = ak.any(mcdf['j_SigJetMask'] == 1, axis=-1)    # [n_events] bool (#FIXME : Bs based, not event based)
            bs_pt_match = ak.to_numpy(ak.flatten(bs_pt[has_match]))
            bs_pt_all   = ak.to_numpy(ak.flatten(bs_pt))

            # ---------- histograms ----------
            pt_bins = np.array([5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 100, 150, 200], dtype=float)
            centers = 0.5 * (pt_bins[1:] + pt_bins[:-1])
            widths  = pt_bins[1:] - pt_bins[:-1]

            n_all, bins = np.histogram(bs_pt_all,   bins=pt_bins)
            n_match, _  = np.histogram(bs_pt_match, bins=pt_bins)
            eff, lo, hi = utils.mathutils.compute_efficiency(n_all, n_match)
            
            eff_graph   = ROOT.TGraphAsymmErrors(len(centers), centers, eff, 0.5*widths, 0.5*widths, eff-lo, hi-eff)
            h_denom     = ROOT.TH1F(f"h_denom_{channel}", "h_denom", len(centers), pt_bins)
            h_num       = ROOT.TH1F(f"h_num_{channel}", "h_num", len(centers), pt_bins)
            h_denom.Sumw2()
            h_num.Sumw2()
            for i in range(len(centers)):
                h_denom.SetBinContent(i+1, n_all[i])
                h_num.SetBinContent(i+1, n_match[i])
                h_denom.SetBinError(i+1, np.sqrt(n_all[i]))
                h_num.SetBinError(i+1, np.sqrt(n_match[i]))
            
            # save the output to a new ROOT file
            out_file = os.path.join(out_dir, f"{name}_{tag}_{channel}_BsJetmatching.root")
            logger.print_info(f"[I/O] Saving histograms to {out_file}")
            f = ROOT.TFile(out_file, "RECREATE")
            f.cd()
            h_denom.Write(f"h_BsGenPt_{channel}_denom")
            h_num.Write(f"h_BsGenPt_{channel}_num")
            eff_graph.Write(f"eff_BsJetPt_{channel}")
            f.Write()
            f.Close()

            ## ---------- plot ----------
            ## pT distribution of signal Bs mesons
            #fig, ax = plt.subplots(figsize=(8, 8),)
            #ax.hist(centers, bins= bins, weights=n_all/widths, histtype='step', color='tab:blue', alpha=0.7,  label='All signal Bs')
            #ax.hist(centers, bins= bins, weights=n_match/widths, histtype='step', color='tab:red', alpha=0.7, label='Matched signal Bs')

            #ax.set_xlabel(r"$p_T^{gen}}$ (GeV)", fontsize=16)
            #ax.set_ylabel("Events", fontsize=16)
            #ax.legend()
            
            #fig.tight_layout()
            #fig.savefig(os.path.join(out_dir, f"{name}_BsPt_distribution.png"))
            ## efficiency
            #fig, ax = plt.subplots(figsize=(8, 8),)
            #ax.errorbar(centers, eff, yerr=[eff-lo, hi-eff],
            #            xerr=0.5*widths, fmt='o', color='k', ecolor='k', elinewidth=1, capsize=2, label=r'efficinecy $\Delta R(B_s, j) < 0.4$')
            #ax.set_xlabel(r"$p_T^{gen}}$ (GeV)", fontsize=16)
            #ax.set_ylabel("Efficiency", fontsize=16)
            #ax.set_ylim(0, 1.2)
            #ax.legend()
            #fig.tight_layout()
            #fig.savefig(os.path.join(out_dir, f"{name}_BsPt_efficiency.png"))

            

            
        

            
            

    