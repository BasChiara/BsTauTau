'''
- Once you have computed the SFs, the selection is fixed! If you change the selection, also Sfs need to be recomputed
--plot_all_jets options is independent from Sfs computation, so you can compute it also after having already copmuted sfs
Data is not well saved in the root file if you don't run with --noblinding option'''
from datetime import datetime
from io_utils import *
#from samples import *
import samples as info_samples
from selection import *
from weights import *
from sf_electron import *
from sf_muon import *
from sf_trigger_dilepton import *
from sf_computation import *
from utils import *
from plotting_utils import *
from histos_baseline import *
from histos_part import histos_combined_scores, histos_max_scores
from part_scores_functions import *
from plotting_flavourbased_utils import *
from histos_part_selections import histos_part_selections


import argparse
import os
import correctionlib
correctionlib.register_pyroot_binding()

nevents = None # Set to None to process all events, or specify a number for a limited range

ROOT.gROOT.SetBatch()   
ROOT.gStyle.SetOptStat(0)

# Silence ROOT's verbose output messages
ROOT.gErrorIgnoreLevel = ROOT.kWarning  # Suppresses Info messages, keeps Warning and Error

# Enable ROOT multithreading for performance (only if processing all events)
if nevents is None:
    import multiprocessing
    n_threads = multiprocessing.cpu_count()
    print(f"Enabling ROOT multithreading with {n_threads} threads")
    ROOT.EnableImplicitMT(n_threads)
    #ROOT.EnableImplicitMT(8)
   
    # Optimize ROOT for performance
    ROOT.gEnv.SetValue("TFile.AsyncPrefetching", "1")  # Enable async prefetching
    ROOT.gEnv.SetValue("TTreeCache.Size", "50000000")  # 50MB cache
    ROOT.gEnv.SetValue("TFile.MaxPrefetchCacheSize", "100000000")  # 100MB prefetch
    ROOT.gEnv.SetValue("RDataFrame.DefaultNSlots", str(n_threads))  # Force RDataFrame to use all cores
else:
    print(f"Multithreading disabled because nevents is limited to {nevents}")
    print("ROOT multithreading doesn't work well with limited event processing")

def parse_arguments():
    parser = argparse.ArgumentParser(description="BsTauTau Plotter")
    parser.add_argument('--channels', nargs='+', default=['emu'], help='Channels to process')
    parser.add_argument('--year', default='2018', choices=info_samples.years, type = str, help='Year of data taking')
    parser.add_argument('--flavor', action='store_true', default=False, help='Enable flavor-based histograms')
    parser.add_argument('--make_histos', action='store_true', default=False, help='Enable sample-based histograms')
    parser.add_argument('--noblinding', action='store_true', default=False, help='Disable blinding')
    parser.add_argument('--not_part_samples', action='store_true', default=False, help='Disable part samples (if you want to plot with old Cecile samples)')
    parser.add_argument('--no_sfs', action='store_true', default=False, help='Disable scale factors')
    parser.add_argument('--compute_sfs', action='store_true', default=False, help='Save snapshots with scale factors (run again for plotting)')
    parser.add_argument('--compute_btag_sfs', action='store_true', default=False, help='Save snapshots with b-tag scale factors (run again for plotting)')
    parser.add_argument('--use_ntuples_with_sfs', action='store_true', default=False, help='Use ntuples with scale factors')
    parser.add_argument('--use_ntuples_with_btag_sfs', action='store_true', default=False, help='Use ntuples with b-tag scale factors') #always use b-tag scale factors ??
    parser.add_argument('--plot_all_jets', action='store_true', default=False, help='Plot all b-tagged jets instead of just top 2 by pT')
    parser.add_argument('--save_filtered_data', action='store_true', default=False, help='Save filtered/processed data for faster reprocessing')
    parser.add_argument('--use_filtered_data', action='store_true', default=False, help='Use previously saved filtered data instead of processing from scratch')
    parser.add_argument('--plot_part_selections', action='store_true', default=False, help='Enable ParT sequential cuts plots (ParTRawTauhtaumu_frac > 0.6)')
    parser.add_argument('--test', action='store_true', default=False, help='Run a quick test with onbly signal sample')
    return parser.parse_args()

tau_scores = ['ParTRawTauhtauh', 'ParTRawTauhtaumu', 'ParTRawTauhtaue']
bkg_scores = ['ParTRawB', 'ParTRawC', 'ParTRawOther', 'ParTRawSingletau']
parT_scores = tau_scores + bkg_scores



def main():

    label = '%s'%(datetime.now().strftime('%d%b%Y_%Hh%Mm%Ss'))
    print("#### Plotting label:", label)
    args = parse_arguments()
    channels = args.channels
    channels = channels[0].split(',')
    year = args.year
    print("---- Processing channels: ", channels)
    no_sfs = args.no_sfs
    compute_sfs = args.compute_sfs #Compute lepton SFs
    compute_btag_sfs = args.compute_btag_sfs # Compute btagging SFs (lep SFs required)
    use_ntuples_with_sfs = args.use_ntuples_with_sfs ##Plot only with lep SFs
    use_ntuples_with_btag_sfs = args.use_ntuples_with_btag_sfs ## Plot with lep Sfs and btagging SFs
    flavor = args.flavor
    make_histos = args.make_histos
    blinding = not args.noblinding
    part_samples = not args.not_part_samples
    plot_all_jets = args.plot_all_jets
    save_filtered_data = args.save_filtered_data
    use_filtered_data = args.use_filtered_data
    plot_part_selections = args.plot_part_selections
    
    
    # Initialize SFs
    declare_sfs_cpp_functions(year)
    
    # Create plot directories --> move later
    if make_histos : make_directories_for_plots(label, channels)

    samples = dict()
    tree_name = 'Events'

    load_invmass()
    load_sorting_functions()
    for ch in channels:
        print("\n=============================")
        print(f"========= Channel {ch} ========")
        print("=============================")

        #tree_dir_data = '/eos/cms/store/cmst3/group/bpark/ccaillol/ntuples_emu_2018_ParT/'
        if not part_samples:
            tree_dir = '/eos/cms/store/cmst3/group/bpark/ccaillol/ntuples_%s_2018'%(ch)
            tree_dir_wsfs= None
            tree_dir_btag_sfs = None
            tree_dir_filtered = None
            info_samples.files_names['tt_semilep'] = 'TTToSemiLeptonic'
            info_samples.files_names['st_tw'] = 'ST_tW_top'
            # Remove 'bstautau' from mc_samples_names if present
            used_mc_samples_names = [name for name in info_samples.mc_samples_names if name != 'bstautau']
        elif args.test:
            print("---- TEST MODE ----")
            tree_dir          = '/eos/cms/store/group/phys_bphys/cbasile/BsTauTau-ttbar/test2018-v2/flat_ntuples/ntuples_%s_2018_ParT'%(ch)
            tree_dir_wsfs     = './tmp_out/wsfs_snapshots/'
            tree_dir_btag_sfs = './tmp_out/btag_sfs_snapshots-sys/'
            tree_dir_filtered = './tmp_out/filtered_data_snapshots/'
            used_mc_samples_names = info_samples.mc_samples_names[:2]  # Only use the first MC sample (e.g., 'bstautau') for testing
        else:
            tree_dir          = '/eos/cms/store/group/phys_bphys/cbasile/BsTauTau-ttbar/test2018-v2/flat_ntuples/ntuples_%s_2018_ParT'%(ch)
            #tree_dir          = '/eos/cms/store/cmst3/group/bpark/friti/bstautau/flat_ntuples/ntuples_%s_2018_ParT'%(ch)
            tree_dir_wsfs     = '%s/wsfs_snapshots/'%(tree_dir)
            tree_dir_btag_sfs = '%s/btag_sfs_snapshots-sys/'%(tree_dir)
            tree_dir_filtered = '%s/filtered_data_snapshots/'%(tree_dir)
            used_mc_samples_names = info_samples.mc_samples_names  # Use all MC samples including 'bstautau'

        print(f"Using tree directory: {tree_dir}")
        samples[ch] = dict()

        # Handle MC samples
        print("\n====== Loading MC Samples ======")
        mc_samples = load_mc_samples(ch, used_mc_samples_names, year, info_samples.files_names, tree_name, tree_dir, tree_dir_wsfs, tree_dir_btag_sfs, info_samples.luminosity_2018, info_samples.cross_sections, trigger_selections, use_ntuples_with_sfs, compute_btag_sfs, use_ntuples_with_btag_sfs, part_samples, nevents)
        samples[ch].update(mc_samples)

        # Handle data samples
        print("\n====== Loading Data Samples ======")
        data_samples, chains = load_data_samples(ch, info_samples.data_samples_names, info_samples.files_names, tree_name, tree_dir, trigger_selections, trigger_exclusions, info_samples.eras_2018, nevents, use_filtered_data, tree_dir_filtered)
        samples[ch].update(data_samples)
        
        print("\n====== Processing Samples ======")
        for k, v in samples[ch].items():
           
            minimum_jet_conditions = '(j_pt > 20 & abs(j_eta)< 2.5 & j_jetid>=2)' # jet pt >20 for btagging SFs

            if 'bstautau' in k:
                bstautau_conditions = {
                    "general":      "SigJetMask",
                    "tauhtauh":     "SigJetMaskTauhtauh",
                    "tauhtaue":     "SigJetMaskTauhtaue",
                    "tauhtaumu":    "SigJetMaskTauhtaumu"
                }
            else:
                bstautau_conditions = None

            #!!!!! MC snapshots already saved and these branches already defined. Be careful if changing jet selections this needs to rerun!!!
            if (not compute_btag_sfs and not use_ntuples_with_sfs and not use_ntuples_with_btag_sfs and not 'data' in k) or (not use_filtered_data and 'data' in k):
                print(f"\t + defining new branches")
                samples[ch][k] = define_invariant_mass_and_mt(samples[ch][k],ch)

                # Define selected_jet branches
                samples[ch][k] = define_jets_with_minimum_selection(samples[ch][k],minimum_jet_conditions, part_samples)

                # Define bstautau mask
                if 'bstautau' in k:
                    samples[ch][k] = define_bstautau_mask(samples[ch][k])

                # Define jets with minimum selection for histograms
                samples[ch][k] = define_jets_with_minimum_selection_for_histos(samples[ch][k], is_bstautau='bstautau' in k, bstautau_conditions=bstautau_conditions, part_samples=part_samples)

                # Define b-tagging conditions for filters (needed for selections)
                samples[ch][k] = define_jets_with_btagging_selection_for_filters(samples[ch][k], part_samples=part_samples)


                # Define Filtering conditions (used in selections)
                samples[ch][k] = define_btagging_conditions(samples[ch][k], ch)
                samples[ch][k] = define_jet_conditions(samples[ch][k], ch,minimum_jet_conditions)

                # Filter the samples
                filter = preselection[ch]
                samples[ch][k] = samples[ch][k].Filter(filter)
                print(f"\t + applying preselection filter: {filter}")

                samples[ch][k] = samples[ch][k].Filter(f"ROOT::VecOps::Any({minimum_jet_conditions})")
                if 'bstautau' in k:
                    samples[ch][k] = samples[ch][k].Filter(f"ROOT::VecOps::Any({bstautau_conditions['general']})")


            # First compute Sfs, after rerun to compute btagging SFs, after rerun for plotting
            # Compute Scale Factors if requested
            if compute_sfs and 'data' not in k:
                print(f"[SFs] computing scale factors for sample {k} in channel {ch}")
                samples[ch][k] = compute_all_scale_factors(samples[ch][k], ch, year, k, info_samples.files_names)

                ## Specify a custom output directory for saving snapshots
                output_dir = tree_dir_wsfs
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                save_samples_with_sfs(samples[ch][k], ch, k, info_samples.files_names, output_dir=output_dir)

            # Compute B-tagging Scale Factors separately if requested
            if compute_btag_sfs and 'data' not in k:
                print(f"[b-tag SFs] computing b-tagging scale factors for sample {k} in channel {ch}")
                if ch == 'mu': # btagging condition is medium for channel mu
                    samples[ch][k] = compute_btagging_scale_factors(samples[ch][k], ch, "M")
                    samples[ch][k] = compute_btagging_event_weight(samples[ch][k], ch, "M")

                else:
                    samples[ch][k] = compute_btagging_scale_factors(samples[ch][k], ch, "L")
                    samples[ch][k] = compute_btagging_event_weight(samples[ch][k], ch, "L")

                ## Specify a custom output directory for saving snapshots.
                output_dir = tree_dir_btag_sfs
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                #plot_event_weight_2d(samples[ch][k], 'sfs_plots/')
                save_samples_with_btagging_sfs(samples[ch][k], ch, k, info_samples.files_names, output_dir=output_dir)


            # FIXME : this part does not work
            # Save filtered data if requested (ONLY for data samples, MC samples are skimmed already after SF computation)
            if save_filtered_data and 'data' in k:
                print(f"Saving filtered data for sample {k} in channel {ch}")
                
                ## Use the new save function that handles eras properly
                output_dir = tree_dir_filtered
                save_filtered_data_snapshot(samples[ch][k], ch, k, info_samples.files_names, output_dir)


            # Define histogram-specific b-tagging branches AFTER filtering (won't be in snapshots)
            samples[ch][k]     = define_jets_with_btagging_selection_for_histos(samples[ch][k], part_samples=part_samples, plot_all_jets=plot_all_jets)
            ## define bstautau mask for different tau decay modes
            if 'bstautau' in k:
                samples[ch][k] = define_bstautau_taudecaymodes_mask(samples[ch][k])
            
            # Define  total event-weight
            if 'data' not in k:
                #weight_str = build_weight_string(k, info_samples.files_names, args)
                #print(f"Applying weights to {k}: {weight_str}")
                #samples[ch][k] = samples[ch][k].Define('tot_weight', weight_str)
                samples[ch][k] = define_total_weight(samples[ch][k], k, info_samples.files_names, args)


            if part_samples: #using updated samples with part scores
                samples[ch][k] = define_combined_scores(samples[ch][k], tau_scores, parT_scores, bkg_scores, 'bstautau' in k, bstautau_conditions)
                #FIXME : at some point I want the save step here save_samples_with_btagging_sfs(samples[ch][k], ch, k, info_samples.files_names, output_dir=output_dir)
                
                if plot_part_selections:
                    # Apply  cuts filter and ONLY use those histograms
                    samples[ch][k] = apply_part_sequential_cuts_filter(samples[ch][k], is_bstautau='bstautau' in k)
                    histos[ch] = {}  # Clear regular histos
                    histos[ch].update(histos_part_selections)  # Only add sequential cuts histos
                    
                    if flavor:
                        histos_flavor[ch] = {}  # Clear regular flavor histos
                        histos_flavor[ch].update(histos_part_selections)  # Only add sequential cuts histos for flavor
                else:
                    # Regular plotting - define all the usual histograms
                    ## Define combined scores histograms
                    histos[ch].update(histos_combined_scores)
                    histos[ch].update(histos_jets_part)
                    histos[ch].update(histos_interesting_jets_part)

                    if flavor:
                        histos_flavor[ch].update(histos_interesting_jets_part)
                        histos_flavor[ch].update(histos_combined_scores)

                    ## define MAX scores
                    samples[ch][k] = define_max_scores(samples[ch][k], parT_scores, 'bstautau' in k, bstautau_conditions)
                    histos[ch].update(histos_max_scores)
                    #histos_flavor[ch].update(histos_max_scores) Not really easy to do because they are filtered in a weird way and I would need to define also hadronFlavor with the same filter
        # -- end loop on samples

        print("##### Creating Histogram Definitions #####")
        # Initialize all histogram definitions BEFORE processing (lazy setup)
        temp_hists = None
        temp_flavor_hists = None
        
        if make_histos:
            print("Setting up sample-based histograms...")
            temp_hists = initialize_histograms(histos, samples, ch)
            if flavor:
                print("Setting up flavor-based histograms...")
                temp_flavor_hists = initialize_flavor_histograms(histos_flavor, samples, ch)

        print("##### Plotting Histograms #####")
        c1, main_pad, ratio_pad = create_canvas_with_pads()
        
        if make_histos and temp_hists:
            print("Processing sample-based histograms...")
            process_histograms(histos, temp_hists, samples, ch, info_samples.colours, label, info_samples.titles, main_pad, ratio_pad, c1, blinding)

        if flavor and temp_flavor_hists:
            print("Processing flavor-based histograms...")
            process_flavor_histograms(histos_flavor, temp_flavor_hists, ch, label, main_pad, ratio_pad, c1, info_samples.colours, blinding)

        print("#### Plotting label:", label)
        print("End channel ", ch, "script at ", datetime.now().strftime('%d%b%Y_%Hh%Mm%Ss'))
    # end of channel loop
    
    print("#### Plotting label:", label)
    print("End of script at ", datetime.now().strftime('%d%b%Y_%Hh%Mm%Ss'))

if __name__ == '__main__':    main()
