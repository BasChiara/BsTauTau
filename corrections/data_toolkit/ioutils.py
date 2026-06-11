import argparse
import os, sys
import ROOT
from . import samples


def checkpath(path, isdir=False, mustexist=True):

    if mustexist and not os.path.exists(path):
        print(f"[ERROR] path {path} does not exist.")
        sys.exit(1)
    else:
        if isdir and not os.path.isdir(path):
            os.makedirs(path)
            print(f"[INFO] created directory {path}")

def get_genEventSumw(file_path):
    """
        Retrieve the sum of genEventSumw from the Runs tree in a ROOT file
    """
    f = ROOT.TFile.Open(file_path)
    runs_tree = f.Get("Runs")
    if not runs_tree:
        raise RuntimeError(f"No Runs tree found in file {file_path}")

    sumw = 0
    for entry in runs_tree:
        sumw += entry.genEventSumw

    print(" [weight] the total enEventSumw is ",sumw)
    f.Close()
    return sumw


def load_mc_samples(indir, mc_samples_names, year, files_names, tree_name, nevents = None):
    """
        Load MC samples, apply weights, and trigger selections.
    """
    outsamples = dict()
    tree_dir_mc = indir

    for k in mc_samples_names:
        
        file_name = os.path.join(tree_dir_mc, files_names[k]+'.root')
        checkpath(file_name, isdir=False, mustexist=True)
        
        print(f" + {file_name}")

        # Create RDataFrame for the sample
        if nevents == None:
            outsamples[k] = ROOT.RDataFrame(tree_name, file_name)
        else:
            outsamples[k] = ROOT.RDataFrame(tree_name, file_name).Range(nevents)
        
        # normalization weight -> FIXME year dependency
      
        norm_weight = samples.luminosity_year[year]['total'] * samples._xsec_samples[k] * 1000 / get_genEventSumw(file_name)
        outsamples[k] = outsamples[k].Define('norm_weight',     f'genWeight*{norm_weight}')
        outsamples[k] = outsamples[k].Define('norm_weightUnc', f'norm_weight*sqrt(({samples.luminosity_year[year]["unc"]}*{samples.luminosity_year[year]["unc"]}) + ({samples._xsec_samples_relunc[k]}*{samples._xsec_samples_relunc[k]}))') # FIXME : use sum in quadrature expr

    
    return outsamples

def load_data_samples(ch, data_samples, files_names, tree_name, tree_dir_data, trigger_selections, trigger_exclusions, eras_2018, nevents = None, use_filtered_data=False, tree_dir_filtered=None):
    """Load data samples and apply trigger selections and exclusions."""
    data_samples_dict = dict()
    chains_dict = dict()  # Store TChain objects to ensure they persist

    # Choose the appropriate directory - ONLY difference when using filtered data
    if use_filtered_data:
        print(f"Using filtered data from: {tree_dir_filtered}")
        data_dir = tree_dir_filtered
    else:
        data_dir = tree_dir_data
    
    if not os.path.isdir(data_dir):
        print(f"Error: Data directory {data_dir} does not exist.")
        return data_samples_dict, chains_dict
    
    for k in data_samples[ch]:
        print(f"\nLoading data sample {k} for channel {ch}")
        file_name = files_names[k]
        tmp_chain = ROOT.TChain(tree_name)

        if use_filtered_data:
            # Only one file, no eras
            era_file = f'{data_dir}/{file_name}.root'
            if not os.path.isfile(era_file):
                print(f"Warning: File {era_file} does not exist. Skipping this era for sample {k}.")
                continue
            print(f" + {era_file}")
            tmp_chain.Add(era_file)
        else:
            # Add the eras for each data sample
            for era in eras_2018: #FIXME: generalize 
                era_file = f'{data_dir}/{file_name}{era}.root'
                if not os.path.isfile(era_file):
                    print(f"Warning: File {era_file} does not exist. Skipping this era for sample {k}.")
                    continue
                print(f" + {era_file}")
                tmp_chain.Add(era_file)

        if nevents == None:
            tmp_data_rdf = ROOT.RDataFrame(tmp_chain)
        else:
            tmp_data_rdf = ROOT.RDataFrame(tmp_chain).Range(nevents)
        # Debug: print number of events loaded 

        # Apply trigger selection and exclusions ONLY if NOT using filtered data
        if not use_filtered_data:
            trigger_selection = trigger_selections[ch][k]
            exclusions = trigger_exclusions[ch][k]
            
            exclusion_filter = ' & '.join([f'!({exclusion})' for exclusion in exclusions]) if exclusions else ''
            final_trigger_filter = f'({trigger_selection}) & ({exclusion_filter})' if exclusion_filter else trigger_selection
            print(f"Applying combined trigger selection and exclusion for {k} in channel {ch}: {final_trigger_filter}")

            filtered_rdf = tmp_data_rdf.Filter(final_trigger_filter)
        else:
            print(f"Using pre-filtered data for {k} - skipping trigger filters")
            filtered_rdf = tmp_data_rdf

        # Normalization for data is just 1
        if not filtered_rdf.HasColumn('tot_weight'):
            filtered_rdf = filtered_rdf.Define('tot_weight', '1')

        # Store both the TChain and the RDataFrame
        data_samples_dict[k] = filtered_rdf
        chains_dict[k] = tmp_chain

    return data_samples_dict, chains_dict
