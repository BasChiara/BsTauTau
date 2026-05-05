"""
Scale Factor computation functions for different physics objects and channels.
"""

from sf_cpp_functions import *
import ROOT
from array import array
import numpy as np

def compute_object_scale_factors(samples, ch, year, k, files_names):
    """
    Compute object scale factors (muon and electron ID, isolation, reconstruction).
    
    Args:
        samples: RDataFrame sample
        ch: Channel name (e.g., 'mu', 'e', 'emu', 'mumu', 'ee')
        k: Sample key
        files_names: Dictionary mapping sample keys to file names
    
    Returns:
        Modified RDataFrame with object scale factors applied
    """
    
    # Muon scale factors
    if ch in ['emu', 'mu', 'mumu']:
        samples = samples.Filter("mu1_pt>20")
        # ID
        samples = samples.Define("mu1_idsf",        'csetMu_id->evaluate({std::abs(mu1_eta), mu1_pt,"nominal"})')
        samples = samples.Define("mu1_idsfUnc",     quadrature_sum_expr(['csetMu_id->evaluate({std::abs(mu1_eta), mu1_pt,"stat"})', 'csetMu_id->evaluate({std::abs(mu1_eta), mu1_pt,"syst"})']))
        # Isolation
        samples = samples.Define("mu1_isosf",       'csetMu_iso->evaluate({std::abs(mu1_eta), mu1_pt,"nominal"})')
        samples = samples.Define("mu1_isosfUnc",    quadrature_sum_expr(['csetMu_iso->evaluate({std::abs(mu1_eta), mu1_pt,"stat"})', 'csetMu_iso->evaluate({std::abs(mu1_eta), mu1_pt,"syst"})']))

        if ch != 'mumu':
            samples = combine_insert_weight(samples, 'mu_sf_weight', ['mu1_idsf', 'mu1_isosf'], make_variations=True)
        
        else : # Second muon for mumu channel
            samples = samples.Filter("mu2_pt>20")
            # ID
            samples = samples.Define("mu2_idsf",        'csetMu_id->evaluate({std::abs(mu2_eta), mu2_pt,"nominal"})')
            samples = samples.Define("mu2_idsfUnc",     quadrature_sum_expr(['csetMu_id->evaluate({std::abs(mu2_eta), mu2_pt,"stat"})', 'csetMu_id->evaluate({std::abs(mu2_eta), mu2_pt,"syst"})']))
            # Isolation
            samples = samples.Define("mu2_isosf",       'csetMu_iso->evaluate({std::abs(mu2_eta), mu2_pt,"nominal"})')
            samples = samples.Define("mu2_isosfUnc",    quadrature_sum_expr(['csetMu_iso->evaluate({std::abs(mu2_eta), mu2_pt,"stat"})', 'csetMu_iso->evaluate({std::abs(mu2_eta), mu2_pt,"syst"})']))
            
            samples = combine_insert_weight(samples, 'mu_sf_weight', ['mu1_idsf', 'mu1_isosf', 'mu2_idsf', 'mu2_isosf'], make_variations=True)
    
    # Electron scale factors
    if ch in ['emu', 'e', 'ee']:
        samples = samples.Filter("e1_pt>20")
        # Reco
        samples = samples.Define("e1_recosf",   'csetEl_all->evaluate({"'+str(year)+'", "sf", "RecoAbove20", std::abs(e1_eta), e1_pt})')
        samples = samples.Define("e1_recosfUnc", syst_fromvar_expr('csetEl_all->evaluate({"'+str(year)+'", "sfup", "RecoAbove20", std::abs(e1_eta), e1_pt})','csetEl_all->evaluate({"'+str(year)+'", "sfdown", "RecoAbove20", std::abs(e1_eta), e1_pt})'))
        # ID
        samples = samples.Define("e1_idsf",     'csetEl_all->evaluate({"'+str(year)+'", "sf", "Tight", std::abs(e1_eta), e1_pt})')
        samples = samples.Define("e1_idsfUnc",   syst_fromvar_expr('csetEl_all->evaluate({"'+str(year)+'", "sfup", "Tight", std::abs(e1_eta), e1_pt})', 'csetEl_all->evaluate({"'+str(year)+'", "sfdown", "Tight", std::abs(e1_eta), e1_pt})'))

        if ch != 'ee':
            samples = combine_insert_weight(samples, 'e_sf_weight', ['e1_recosf', 'e1_idsf'], make_variations=True)
        else: # Second electron for ee channel
            samples = samples.Filter("e2_pt>20")
            
            # Reco
            samples = samples.Define("e2_recosf",   'csetEl_all->evaluate({"'+str(year)+'", "sf", "RecoAbove20", std::abs(e2_eta), e2_pt})')
            samples = samples.Define("e2_recosfUnc", syst_fromvar_expr('csetEl_all->evaluate({"'+str(year)+'", "sfup", "RecoAbove20", std::abs(e2_eta), e2_pt})','csetEl_all->evaluate({"'+str(year)+'", "sfdown", "RecoAbove20", std::abs(e2_eta), e2_pt})'))
            # ID
            samples = samples.Define("e2_idsf",     'csetEl_all->evaluate({"{}", "sf", "Tight", std::abs(e2_eta), e2_pt})')
            samples = samples.Define("e2_idsfUnc",  syst_fromvar_expr('csetEl_all->evaluate({"'+str(year)+'", "sfup", "Tight", std::abs(e2_eta), e2_pt})', 'csetEl_all->evaluate({"'+str(year)+'", "sfdown", "Tight", std::abs(e2_eta), e2_pt})'))
            
            samples = combine_insert_weight(samples, 'e_sf_weight', ['e1_recosf', 'e1_idsf', 'e2_recosf', 'e2_idsf'], make_variations=True)
    
    return samples


def compute_trigger_scale_factors(samples, year, ch):
    """
    Compute trigger scale factors for different channels.
    
    Args:
        samples: RDataFrame sample
        ch: Channel name (e.g., 'mu', 'e', 'emu', 'mumu', 'ee')
    
    Returns:
        Modified RDataFrame with trigger scale factors applied
    """
    
    if ch == 'mu': 
        samples = samples.Filter("mu1_pt>25") 
        samples = samples.Define("mu1_trgsf", 'csetMu_trg->evaluate({std::abs(mu1_eta), mu1_pt,"nominal"})')
        samples = samples.Define('mu1_trgsfUnc', quadrature_sum_expr(['csetMu_trg->evaluate({std::abs(mu1_eta), mu1_pt,"stat"})', 'csetMu_trg->evaluate({std::abs(mu1_eta), mu1_pt,"syst"})']))
        
        samples = combine_insert_weight(samples, 'tot_sf_weight', ['mu_sf_weight', 'mu1_trgsf'], make_variations=True)

    elif ch == 'mumu':
        samples = samples.Define("trg_sf_weight",    "get_mumu_trigger_sf(mu1_pt, mu2_pt)")
        samples = samples.Define('trg_sf_weightUnc', "get_mumu_trigger_sf(mu1_pt, mu2_pt, "+str(year)+",true)")
        
        samples = combine_insert_weight(samples, 'tot_sf_weight', ['mu_sf_weight', 'trg_sf_weight'], make_variations=True)

    elif ch == 'emu':
        samples = samples.Define("trg_sf_weight",    'get_emu_trigger_sf(e1_pt, mu1_pt)')
        samples = samples.Define('trg_sf_weightUnc', 'get_emu_trigger_sf(e1_pt, mu1_pt, "'+str(year)+'",true)')
        
        samples = combine_insert_weight(samples, 'tot_sf_weight', ['mu_sf_weight', 'e_sf_weight', 'trg_sf_weight'], make_variations=True)

    elif ch == 'ee':
        samples = samples.Define("trg_sf_weight",    "get_ee_trigger_sf(e1_pt, e2_pt)")
        samples = samples.Define('trg_sf_weightUnc', "get_ee_trigger_sf(e1_pt, e2_pt, "+str(year)+",true)")
        
        samples = combine_insert_weight(samples, 'tot_sf_weight', ['e_sf_weight', 'trg_sf_weight'], make_variations=True)
    elif ch == 'e':
        samples = samples.Define("e1_trgsf", 'get_single_e_trigger_sf(e1_pt,e1_eta)')
        samples = samples.Define('e1_trgsfUnc', 'get_single_e_trigger_sf(e1_pt,e1_eta, '+str(year)+', true)')
        
        samples = combine_insert_weight(samples, 'tot_sf_weight', ['e_sf_weight', 'e1_trgsf'], make_variations=True)
    
    return samples


def compute_additional_scale_factors(samples, k, files_names):
    """
    Compute additional scale factors like top pT reweighting.
    
    Args:
        samples: RDataFrame sample
        k: Sample key
        files_names: Dictionary mapping sample keys to file names
    
    Returns:
        Modified RDataFrame with additional scale factors applied
    """
    
    # Top pT reweighting for TTbar samples
    if 'TTT' in files_names[k] or 'BsToTauTau' in files_names[k]:
        samples = samples.Define("top_pt_weight", "top_ptweight(GenCand_pt, GenCand_id)")
        samples = samples.Define("top_pt_weightUnc", "fabs(1-top_pt_weight)") # FIXME not sure is correct
    
    return samples


def compute_all_scale_factors(samples, ch, year, k, files_names):
    """
    Main function to compute all scale factors for a given sample.
    
    Args:
        samples: RDataFrame sample
        ch: Channel name (e.g., 'mu', 'e', 'emu', 'mumu', 'ee')
        k: Sample key
        files_names: Dictionary mapping sample keys to file names
    
    Returns:
        Modified RDataFrame with all scale factors applied
    """
    
    # Compute object scale factors
    print(f"\tobject scale factors")
    samples = compute_object_scale_factors(samples, ch, year, k, files_names)
    
    # Compute trigger scale factors
    print(f"\ttrigger scale factors")
    samples = compute_trigger_scale_factors(samples, year, ch)
    
    # Compute additional scale factors
    print(f"\tadditional scale factors")
    samples = compute_additional_scale_factors(samples, k, files_names)
    
    return samples


def save_samples_with_sfs(samples, ch, k, files_names, output_dir):
    """
    Save processed samples with scale factors to disk.
    
    Args:
        samples: RDataFrame sample with scale factors applied
        ch: Channel name
        k: Sample key
        files_names: Dictionary mapping sample keys to file names
    """

    output_path = f"{output_dir}{files_names[k]}.root"
    samples.Snapshot("Events", output_path)
    print(f"[SFs] saved sample with SFs: {output_path}")


## btagging scale factors
def compute_btagging_scale_factors(samples, ch, wp="L"):
    # btagging scale factors depending on btagging selection conditions in various channels
    # wp: working point, "L" (loose) or "M" (medium)
    
    samples = samples.Define("bcjet_mask",      "selected_jets_for_histo_hadronFlavour != 0")
    samples = samples.Define("bcjet_flavour",   "selected_jets_for_histo_hadronFlavour[bcjet_mask]")
    samples = samples.Define("bcjet_eta",       "selected_jets_for_histo_eta[bcjet_mask]")
    samples = samples.Define("bcjet_pt",        "selected_jets_for_histo_pt[bcjet_mask]")
    samples = samples.Define(
        "btag_sf_bcjets",
        f'evaluate_btag_mujets_sf(bcjet_flavour, bcjet_eta, bcjet_pt, "{wp}")'
    )

    samples = samples.Define("lightjet_mask",    "selected_jets_for_histo_hadronFlavour == 0")
    samples = samples.Define("lightjet_flavour", "selected_jets_for_histo_hadronFlavour[lightjet_mask]")
    samples = samples.Define("lightjet_eta",     "selected_jets_for_histo_eta[lightjet_mask]")
    samples = samples.Define("lightjet_pt",      "selected_jets_for_histo_pt[lightjet_mask]")
    samples = samples.Define(
        "btag_sf_lightjets",
        f'evaluate_btag_incl_sf(lightjet_flavour, lightjet_eta, lightjet_pt, "{wp}")'
    )

    samples = samples.Define(
        "btag_sf",
        "merge_btag_sfs(selected_jets_for_histo_hadronFlavour, btag_sf_bcjets, btag_sf_lightjets)"
    )
    
    return samples

def compute_btagging_event_weight(samples, ch, wp):
    # for the moment only loose btagging is used
    if wp == 'L':
        threshold = 0.0499  # Loose working point threshold
    elif wp == 'M':
        threshold = 0.2770  # Medium working point threshold
    samples = samples.Define(
        "btag_event_weight",
        f'compute_event_weight(selected_jets_for_histo_deepflavB, {threshold}, btag_sf, selected_jets_for_histo_hadronFlavour, selected_jets_for_histo_eta, selected_jets_for_histo_pt, "{wp}")'
    )
 
    return samples

def plot_event_weight_2d(samples, output_path):
    """
    Make a 2D histogram of event weights vs |eta| and pt, and save it as an image.

    Args:
        samples: RDataFrame sample with event weights defined
        output_path: Path to save the plot (e.g., 'event_weight_2d.png')
    """

    # Define custom binning
    pt_bins = array('f', [5., 20., 30., 40., 60., 80., 140., 200., 300., 500., 1000.])
    eta_bins = array('f', [0.0, 0.8, 1.6, 2.5])
    n_pt_bins = len(pt_bins) - 1
    n_eta_bins = len(eta_bins) - 1

    # Create the 2D histogram with custom bins
    h2 = ROOT.TH2F(
        "h2_event_weight",
        "Event Weight;|#eta|;p_{T} [GeV]",
        n_eta_bins, eta_bins,
        n_pt_bins, pt_bins
    )

    # Fill histogram from RDataFrame
    # Use selected jets, flatten arrays if needed
    arr_eta = samples.AsNumpy(["selected_jets_for_histo_eta"])["selected_jets_for_histo_eta"]
    arr_pt = samples.AsNumpy(["selected_jets_for_histo_pt"])["selected_jets_for_histo_pt"]
    arr_weight = samples.AsNumpy(["btag_event_weight"])["btag_event_weight"]

    # Flatten arrays if they are jagged (lists of lists)
    eta_flat = np.concatenate(arr_eta) if isinstance(arr_eta[0], (list, np.ndarray)) else arr_eta
    pt_flat = np.concatenate(arr_pt) if isinstance(arr_pt[0], (list, np.ndarray)) else arr_pt
    weight_flat = np.concatenate(arr_weight) if isinstance(arr_weight[0], (list, np.ndarray)) else arr_weight

    # Fill histogram
    for eta, pt, w in zip(eta_flat, pt_flat, weight_flat):
        print(eta, pt, w)  # Debugging line to check values being filled
        h2.Fill(abs(eta), pt, w)

    # Draw and save the histogram
    c = ROOT.TCanvas("c", "c", 800, 600)
    h2.Draw("COLZ")
    c.SaveAs(output_path/"event_btag_weight_2d.png")
    print(f"Saved 2D event weight plot: {output_path}/event_btag_weight_2d.png")

def save_samples_with_btagging_sfs(samples, ch, k, files_names, output_dir):
    """
    Save processed samples with scale factors to disk.
    
    Args:
        samples: RDataFrame sample with scale factors applied
        ch: Channel name
        k: Sample key
        files_names: Dictionary mapping sample keys to file names
    """
    output_path = f"{output_dir}{files_names[k]}.root"
    samples.Snapshot("Events", output_path)
    print(f"Saved sample with b-tagging SFs: {output_path}")


