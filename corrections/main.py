"""
    - apply SFs to the ntuples
"""
import os, sys
import argparse
import ROOT
import uproot
import numpy as np

nevents = 11

# custom imports
import data_toolkit as data
import sf_toolkit as sf


ROOT.gROOT.SetBatch()   
ROOT.gStyle.SetOptStat(0)

# Silence ROOT's verbose output messages
ROOT.gErrorIgnoreLevel = ROOT.kWarning  # Suppresses Info messages, keeps Warning and Error

# Enable ROOT multithreading for performance (only if processing all events)
if nevents is None:
    import multiprocessing
    n_threads = multiprocessing.cpu_count()
    print(f"[ROOT] Enabling ROOT multithreading with {n_threads} threads\n")
    ROOT.EnableImplicitMT(n_threads)
   
    # Optimize ROOT for performance
    ROOT.gEnv.SetValue("TFile.AsyncPrefetching", "1")  # Enable async prefetching
    ROOT.gEnv.SetValue("TTreeCache.Size", "50000000")  # 50MB cache
    ROOT.gEnv.SetValue("TFile.MaxPrefetchCacheSize", "100000000")  # 100MB prefetch
    ROOT.gEnv.SetValue("RDataFrame.DefaultNSlots", str(n_threads))  # Force RDataFrame to use all cores

    # Optimize snapshot writing
    opts = ROOT.RDF.RSnapshotOptions()
    opts.fCompressionLevel = 1  # faster write, slightly larger file
    opts.fCompressionAlgorithm = ROOT.ROOT.kLZ4  # LZ4 is much faster than default ZLIB
else:
    print(f"Multithreading disabled because nevents is limited to {nevents}")
    print("ROOT multithreading doesn't work well with limited event processing")

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
    parser.add_argument("--test", "-t",
                        action="store_true",
                        help="Run in test mode (process only a small subset of events)",
                        )
    return parser.parse_args()


if __name__ == "__main__":

    # process arguments
    args = parse_arguments()
    if os.path.isfile(args.input): in_info = data.samples.parse_inyml(args.input)
    else : print(f"Error: Input file {args.input} does not exist."); sys.exit(1)
    channels   = args.channels
    year       = str(in_info.get('year', 2018))
    _testmode_ = args.test


    #  get samples
    tree_dir_base = in_info.get('MC', {}).get('inpath_template', None)
    out_dir_base  = args.outdirectory if args.outdirectory is not None else in_info.get('MC', {}).get('outpath_template', None)

    used_mc_samples_names = data.samples.mc_samples_names
    if (_testmode_):
        print(" TEST MODE ENABLED")
        used_mc_samples_names = used_mc_samples_names[:1]
    
    print(f" > Processing {len(used_mc_samples_names)} MC samples for channels {channels}: {used_mc_samples_names}")

    samples = dict()
    _tree_name = in_info.get('MC', {}).get('treename', 'Events')

    for ch in channels:
        print(f"\n--------- CHANNEL {ch} ---------")
        
        samples[ch] = dict()
        
        print(" ... loading MC samples")
        tree_dir = tree_dir_base.format(channel=ch)
        data.ioutils.checkpath(tree_dir, isdir=True, mustexist=True)
        out_dir  = out_dir_base.format(channel=ch)
        data.ioutils.checkpath(out_dir, isdir=True, mustexist=False)
        print(f" + {tree_dir}")

        mc_samples = data.ioutils.load_mc_samples(
            tree_dir,
            used_mc_samples_names,
            year,
            data.samples.files_names,
            _tree_name,
            nevents = nevents
        )
        samples[ch].update(mc_samples)
        
        print ("\n--------- PROCESSING SAMPLES ---------\n")
        for name, rdf in samples[ch].items():
            print(f"\n>[{name}]")
            samples[ch][name] = samples[ch][name].Define("entry_idx", "rdfentry_")
        
            # trigger selections (OR of the requirements in data)
            hlt_conditions = data.selection.trigger_selections.get(ch, {})
            hlt_paths      = [hlt_conditions.get(dset, "(1)") for dset in hlt_conditions]
            hlt_sel        = ' | '.join(hlt_paths)
            print(f" [SKIM] trigger selection: {hlt_sel}")

            samples[ch][name] = samples[ch][name].Filter(hlt_sel)

            # define invariant mass and transverse mass
            samples[ch][name] = data.defutils.define_invariant_mass_and_mt(samples[ch][name], ch)
            
            # define jets passing minimal kinematics and b-tagging conditions
            jet_sel = data.selection.min_jet_selection.get(ch, "(1)")
            samples[ch][name] = data.defutils.define_jets_with_minimum_selection(
                samples[ch][name], 
                jet_sel
            )
            #FIXME : check if anything missing for Bs signal
            if 'bstautau' in name: samples[ch][name] = data.defutils.define_bstautau_mask(samples[ch][name])

            samples[ch][name] = data.defutils.define_jets_with_minimum_selection_for_histos(
                samples[ch][name], 
                is_bstautau='bstautau' in name, 
                bstautau_conditions=data.selection.bstautau_conditions
            )
            samples[ch][name] = data.defutils.define_jets_with_btagging_selection_for_filters(samples[ch][name])
            samples[ch][name] = data.defutils.define_btagging_conditions(samples[ch][name], ch) # FIXME : saves conditions for all channels | external dep form btagging cond.
            samples[ch][name] = data.defutils.define_jet_conditions(samples[ch][name], ch, jet_sel) # FIXME : saves conditions for all channels | external dep form jet cond.
            
            # preselections
            pre_sel = data.selection.preselection.get(ch, "(1)")
            print(f" [SKIM] preselection: {pre_sel}")
            samples[ch][name] = samples[ch][name].Filter(pre_sel)

            # jet conditions
            print(f" [SKIM] jet selection: {jet_sel}")
            samples[ch][name] = samples[ch][name].Filter(f"ROOT::VecOps::Any({jet_sel})")


            # save snapshot
            print("\n--------- SAVE (TMP) OUTPUT ---------")
            tmp_outdir  = "tmp_output"
            tmp_outpath = os.path.join(tmp_outdir, f"tmp_{name}.root")
            samples[ch][name].Snapshot(_tree_name, tmp_outpath)
            if os.path.isfile(tmp_outpath):
                print(f"[OUTPUT] Saved processed sample to {tmp_outpath}")
            else:
                print(f"[ERROR] Failed to save processed sample to {tmp_outpath}")

            # open tmp sanpshot with uproot to apply scale factors
            print(f"\n--------- COMPUTE SCALE FACTORS ---------")
            orig_branches, new_branches = {} , {}
            with uproot.open(tmp_outpath) as f:
                tree = f[_tree_name]
                entry_idx  = tree["entry_idx"].array(library="np")
                assert np.all(np.diff(entry_idx) > 0), "entry_idx should be a sequence of consecutive integers starting from 0"
                print(f" + {tree.num_entries} events read from {tmp_outpath}")

                # object scale factors
                objsf_branches = sf.sf_computation.compute_obj_sf(tree, ch, year)
                new_branches.update(objsf_branches)

                # trigger scale factors
                trgsf_branches  = sf.sf_computation.compute_trigger_sf(tree, ch, year)
                new_branches.update(trgsf_branches)

                # top pT re-weight in ttbar
                topsf_branches = sf.sf_computation.compute_top_pTreweight(tree, 'tt' in name or 'bstautau' in name)
                new_branches.update(topsf_branches)

                print(new_branches)
                
            # save new branches with SFs to a new root file
            sfs_outpath = os.path.join(tmp_outdir, f"tmp_{name}_onlysfs.root")
            with uproot.recreate(sfs_outpath) as outf:
                outf[_tree_name] = new_branches
                print(f"[OUTPUT] saved sample with SFs to {sfs_outpath}")
            
            # merge back with RDatFrame
            outpath = os.path.join(tmp_outdir, f"{name}_wsfs.root")
            main_file = ROOT.TFile.Open(tmp_outpath)
            main_tree = main_file.Get(_tree_name)
            main_tree.AddFriend(_tree_name, sfs_outpath)

            rdf_main = ROOT.RDataFrame(main_tree)
            rdf_main.Snapshot(_tree_name, outpath)
