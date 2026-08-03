"""
    - apply preselection and jet selection
    - apply SFs to the ntuples
"""
import os, sys
import multiprocessing
import numpy as np
import time
import argparse

import ROOT
ROOT.gROOT.SetBatch()   
ROOT.gStyle.SetOptStat(0)
ROOT.gErrorIgnoreLevel = ROOT.kWarning  # Suppresses Info messages, keeps Warning and Error
import uproot
BATCH_SIZE  = int(1e5) # number of events to process in each chunk for SF computation
NTHREADS    = multiprocessing.cpu_count()

# custom imports
import data_toolkit as data
import sf_toolkit as sf
import utils

def setup_multithreading(nevents):
    # Enable multithreading for performance (only if processing all events)
    # uproot
    if nevents is None:
        # ROOT
        utils.logger.print_info(f"[ROOT] Enabling ROOT multithreading with {NTHREADS} threads\n")
        ROOT.EnableImplicitMT(NTHREADS)
        # Optimize ROOT for performance
        ROOT.gEnv.SetValue("TFile.AsyncPrefetching", "1")  # Enable async prefetching
        ROOT.gEnv.SetValue("TTreeCache.Size", "50000000")  # 50MB cache
        ROOT.gEnv.SetValue("TFile.MaxPrefetchCacheSize", "100000000")  # 100MB prefetch
        ROOT.gEnv.SetValue("RDataFrame.DefaultNSlots", str(NTHREADS))  # Force RDataFrame to use all cores
        # Optimize snapshot writing
        opts = ROOT.RDF.RSnapshotOptions()
        opts.fCompressionLevel = 1  # faster write, slightly larger file
        opts.fCompressionAlgorithm = ROOT.ROOT.kLZ4  # LZ4 is much faster than default ZLIB
    else:
        utils.logger.print_info(f"Multithreading disabled because nevents is limited to {nevents}")
        utils.logger.print_info("ROOT multithreading doesn't work well with limited event processing")

def parse_arguments():

    defaults_ = {
        "input": None,
        "outdirectory": None,
        "channels": ['emu'],
        "test": False
    }

    parser = argparse.ArgumentParser(description="Apply corrections to ntuples")
    parser.add_argument("--input", "-i", 
                        required=True, 
                        help=".yml file containing the input ntuples locations and metadata"
                        )
    parser.add_argument("--outdirectory", "-o",
                        default=defaults_["outdirectory"],
                        help=f"directory for output-ntuples (created if does not exist). N.B. overwrites the location in the input .yml file if provided. | DEFAULT = {defaults_['outdirectory']}",
                        )
    parser.add_argument('--channels', 
                        nargs='+', 
                        default=defaults_["channels"],
                        help=f'select channels to process. | DEFAULT = {defaults_["channels"]}')
    parser.add_argument("--test", "-t",
                        action="store_true",
                        help=f"run in test mode (process only a small subset of events). | DEFAULT = {defaults_['test']}",
                        )
    return parser.parse_args()


if __name__ == "__main__":

    init_time = time.time()

    # process arguments
    args = parse_arguments()
    
    if os.path.isfile(args.input): in_info = data.samples.parse_inyml(args.input)
    else : utils.logger.print_error(f"Error: Input file {args.input} does not exist."); sys.exit(1)
    
    channels   = args.channels
    year       = str(in_info.get('common', {}).get('year', 2018))
    _testmode_ = args.test
    nevents    = 1000 if _testmode_ else None
    setup_multithreading(nevents)


    #  get samples
    tree_dir_base = in_info.get('MC', {}).get('inpath_template', None)
    out_dir_base  = args.outdirectory if args.outdirectory else in_info.get('MC', {}).get('outpath_template', None)
    tmp_outdir    = "/tmp" if not _testmode_ else "tmp_output" # temporary path for RDataFrame -> uproot


    used_mc_samples_names = data.samples.mc_samples_names
    if (_testmode_):
        utils.logger.print_info(" TEST MODE ENABLED")
        used_mc_samples_names = used_mc_samples_names[:1] # test only one MC sample
    
    print(f" > Processing {len(used_mc_samples_names)} MC samples for channels {channels}: {used_mc_samples_names}")

    samples = dict()
    _tree_name = in_info.get('common', {}).get('treename', 'Events')

    # --> LOOP ON CHANNELS
    for ch in channels:
        utils.logger.print_bold(f"\n--------- CHANNEL {ch} ---------")
        
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
        
        utils.logger.print_bold(f"\n>>> PROCESSING SAMPLES")
        # --> LOOP ON SAMPLES
        for name, rdf in samples[ch].items():
            print(f"\n------ {name} ------")
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


            # --- save temporary snapshot
            utils.logger.print_info("[TMP] save temporary snapshot .....")
            if not os.path.exists(tmp_outdir):
                os.makedirs(tmp_outdir)
            tmp_outpath = os.path.join(tmp_outdir, f"tmp_{data.samples.files_names[name]}.root")
            samples[ch][name].Snapshot(_tree_name, tmp_outpath)
            if os.path.isfile(tmp_outpath):
                utils.logger.print_info(f"[TMP] Saved processed sample to {tmp_outpath}")
            else:
                utils.logger.print_error(f"[TMP] Failed to save processed sample to {tmp_outpath}")
                sys.exit(1)

            # reference: full entry_idx set + count from the RDF snapshot ---
            with uproot.open(tmp_outpath) as f:
                tree = f[_tree_name]
                n_events_in   = tree.num_entries
                entry_idx_in  = tree["entry_idx"].array(library="np")
                print(f" + {n_events_in} events read from {tmp_outpath}")
            if n_events_in == 0:
                print(f"[{name}] 0 events survive selection — skipping SF step, writing empty tree")
                continue
            # sanity: tmp output itself shouldn't have duplicates (defensive, cheap)
            assert len(np.unique(entry_idx_in)) == n_events_in, \
                f"[{name}] duplicate entry_idx already present in {tmp_outpath} before SF processing"

            # --- SF COMPUTATION (chunked) ---
            utils.logger.print_bold(f"\n--------- COMPUTE SCALE FACTORS ---------") 
            sfs_outpath = os.path.join(tmp_outdir, f"tmp_{data.samples.files_names[name]}_onlysfs.root")
            n_events_out = 0
            with uproot.recreate(sfs_outpath) as outf:
                writer = None
                #with uproot.open(tmp_outpath) as f:
                for chunk in uproot.iterate(f"{tmp_outpath}:{_tree_name}", step_size=BATCH_SIZE, library="ak"):
                    #tree = f[_tree_name]
                    #entry_idx  = tree["entry_idx"].array(library="np")
                    #assert np.all(np.diff(entry_idx) > 0), "entry_idx should be a sequence of consecutive integers starting from 0"
                    #print(f" + {tree.num_entries} events read from {tmp_outpath}")

                    # object scale factors
                    objsf_branches, objsf_w = sf.sf_computation.compute_obj_sf(chunk, ch, year)

                    # trigger scale factors
                    trgsf_branches = sf.sf_computation.compute_trigger_sf(chunk, ch, year)

                    # top pT re-weight in ttbar
                    topsf_branches = sf.sf_computation.compute_top_pTreweight(chunk, 'tt' in name or 'bstautau' in name)

                    # b-tag scale factors
                    btagsf_branches = sf.sf_computation.compute_btag_sf(chunk, ch, year, 
                                                                        jetbranch   = "selected_jets_for_histo", 
                                                                        wp          = data.selection.btag_chwp[ch][0],
                                                                        wp_val      = data.selection.btag_chwp[ch][1]
                                                                        )
                    out_chunk = {
                        "entry_idx": chunk["entry_idx"], # keep entry-by-entry alignement
                        **objsf_branches, 
                        **trgsf_branches, 
                        **topsf_branches, 
                        **btagsf_branches,
                    }

                    n_events_out += len(chunk)
                
                    if writer is None:
                        outf[_tree_name] = out_chunk
                        writer = outf[_tree_name]
                    else:
                        writer.extend(out_chunk)
                if _testmode_:
                    print(out_chunk.keys())
            utils.logger.print_info(f"[TMP] saved sample with SFs to {sfs_outpath}")
            
            # --- post-loop consistency check: no loss, no duplication, same events ---
            with uproot.open(sfs_outpath) as f2:
                tree_out       = f2[_tree_name]
                n_events_check = tree_out.num_entries
                entry_idx_out  = tree_out["entry_idx"].array(library="np")
            
            if not np.array_equal(entry_idx_in, entry_idx_out): # entry_idx should be identical between the tmp snapshot and the SF snapshot
                raise RuntimeError(f"[{name}] entry_idx ORDER differs between {tmp_outpath} and {sfs_outpath} — AddFriend alignment is broken")
            if not (n_events_out == n_events_in == n_events_check): # same event count in tmp snapshot, chunked SF processing, and reopened SF snapshot
                raise RuntimeError(f"[{name}] event count mismatch: tmp={n_events_in} | chunked_written={n_events_out} | reopened={n_events_check}")
            if not (len(np.unique(entry_idx_out)) == n_events_out): # no duplicates in the SF snapshot
                raise RuntimeError(f"[{name}] duplicate entry_idx in {sfs_outpath} — a chunk was likely processed/written twice")
            utils.logger.print_success(f"[CHECK] {n_events_out} events consistent between {tmp_outpath} and {sfs_outpath}: no loss, no duplication")

            # --- merge SFs into the main tree and save final snapshot ---
            outpath  = os.path.join(tmp_outdir if _testmode_ else out_dir,
                                    f"{data.samples.files_names[name]}.root")

            # Disable MT for the final merge
            if not _testmode_:
                ROOT.DisableImplicitMT()

            sf_file  = ROOT.TFile.Open(sfs_outpath)
            sf_tree  = sf_file.Get(_tree_name)
            sf_tree.ResetBit(ROOT.TTree.kEntriesReshuffled)

            main_file = ROOT.TFile.Open(tmp_outpath)
            main_tree = main_file.Get(_tree_name)
            main_tree.ResetBit(ROOT.TTree.kEntriesReshuffled)
            main_tree.AddFriend(sf_tree)

            rdf_main = ROOT.RDataFrame(main_tree)
            rdf_main.Snapshot(_tree_name, outpath)

            if os.path.isfile(outpath):
                utils.logger.print_success(f"[OUTPUT] Saved final processed sample to {outpath}")
                # clean up temporary files
                os.remove(tmp_outpath)
                os.remove(sfs_outpath)
                utils.logger.print_info(f"[CLEANUP] Removed temporary files {tmp_outpath} and {sfs_outpath}")
            else:
                utils.logger.print_error(f"Failed to save final processed sample to {outpath}")
                sys.exit(1)
            
            if not _testmode_:
                ROOT.EnableImplicitMT(NTHREADS)  # restore for next sample

    end_time = time.time()
    elapsed_time = end_time - init_time
    utils.logger.print_bold(f"\n>>> DONE in {elapsed_time:.2f}'' ({elapsed_time/60:.2f}')")
