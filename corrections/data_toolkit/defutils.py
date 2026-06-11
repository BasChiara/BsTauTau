import ROOT
from .defcpp_functions import *


jet_attributes_global = [
        "pt", "eta", "phi", "m", "puid", "jetid", "deepflavB", "hadronFlavour"]

jet_attributes_part = ["ParTRawB", "ParTRawC", "ParTRawOther", "ParTRawSingletau",
        "ParTRawTauhtaue", "ParTRawTauhtauh", "ParTRawTauhtaumu"]

# Define b-tagging thresholds
btag_thresholds = {
    "medium": 0.2770,
    "loose": 0.049
}

def define_bstautau_mask(samples):
    samples = (
                    samples
                    .Define("SignalBs", "findIndicesOfBsTauTau(GenCand_isBsTauTau)")
                    .Define("SigJetIdx", f"matchSignalBsToJets(SignalBs, GenCand_eta, GenCand_phi, selected_jets_pt, selected_jets_eta, selected_jets_phi, selected_jets_deepflavB, {btag_thresholds['loose']})")
                    .Define("SigJetMask", "maskFromIndices(SigJetIdx, selected_jets_pt.size())")
                )
    return samples

def define_bstautau_taudecaymodes_mask(samples):

    samples = (
        samples
        .Define("SignalBsTauhtauh", "findIndicesOfBsTauTau(GenCand_isBsTauTauh)")
        .Define("SigJetIdxTauhtauh", 
                f"matchSignalBsToJets(SignalBsTauhtauh, GenCand_eta, GenCand_phi, "
                f"btagged_loose_jets_pt_above_20_for_histo_pt, btagged_loose_jets_pt_above_20_for_histo_eta, btagged_loose_jets_pt_above_20_for_histo_phi, "
                f"btagged_loose_jets_pt_above_20_for_histo_deepflavB, {btag_thresholds['loose']})")
        .Define("SigJetMaskTauhtauh", "maskFromIndices(SigJetIdxTauhtauh, btagged_loose_jets_pt_above_20_for_histo_pt.size())")
    )

    # For Tauhtaue
    samples = (
        samples
        .Define("SignalBsTauhtaue", "findIndicesOfBsTauTau(GenCand_isBsTauTaue)")
        .Define("SigJetIdxTauhtaue", 
                f"matchSignalBsToJets(SignalBsTauhtaue, GenCand_eta, GenCand_phi, "
                f"btagged_loose_jets_pt_above_20_for_histo_pt, btagged_loose_jets_pt_above_20_for_histo_eta, btagged_loose_jets_pt_above_20_for_histo_phi, "
                f"btagged_loose_jets_pt_above_20_for_histo_deepflavB, {btag_thresholds['loose']})")
        .Define("SigJetMaskTauhtaue", "maskFromIndices(SigJetIdxTauhtaue, btagged_loose_jets_pt_above_20_for_histo_pt.size())")
    )
    
    # For Tauhtaumu
    samples = (
        samples
        .Define("SignalBsTauhtaumu", "findIndicesOfBsTauTau(GenCand_isBsTauTaumu)")
        .Define("SigJetIdxTauhtaumu",
                f"matchSignalBsToJets(SignalBsTauhtaumu, GenCand_eta, GenCand_phi, "
                f"btagged_loose_jets_pt_above_20_for_histo_pt, btagged_loose_jets_pt_above_20_for_histo_eta, btagged_loose_jets_pt_above_20_for_histo_phi, "
                f"btagged_loose_jets_pt_above_20_for_histo_deepflavB, {btag_thresholds['loose']})")
        .Define("SigJetMaskTauhtaumu", "maskFromIndices(SigJetIdxTauhtaumu, btagged_loose_jets_pt_above_20_for_histo_pt.size())")
    )

    return samples


def define_jets_with_minimum_selection(samples, minimum_jet_conditions, part_samples = True):
    """Function to define jet-related branches."""

    # Define branches for each jet attribute
    if part_samples:
        jet_attributes = jet_attributes_global + jet_attributes_part
    else:
        jet_attributes = jet_attributes_global

    for attr in jet_attributes:
        samples = samples.Define(f"selected_jets_{attr}", f"j_{attr}[{minimum_jet_conditions}]")

    samples = samples.Define("selected_njets", "selected_jets_pt.size()")


    return samples

def define_jets_with_minimum_selection_for_histos(samples, is_bstautau, bstautau_conditions, part_samples=True):

    '''Prepare branches selected for bstautau specific case (only jets matching with bs->tautau)'''
    if part_samples:
        jet_attributes = jet_attributes_global + jet_attributes_part
    else:
        jet_attributes = jet_attributes_global

    if is_bstautau:
        for attr in jet_attributes:
            samples = samples.Define(f"selected_jets_for_histo_{attr}", f"selected_jets_{attr}[{bstautau_conditions['general']}]")

    else:
        for attr in jet_attributes:
            samples = samples.Define(f"selected_jets_for_histo_{attr}", f"selected_jets_{attr}")    


    samples = samples.Define("selected_jets_for_histo_njets", "selected_jets_for_histo_pt.size()")

    return samples


def define_jets_with_btagging_selection_for_filters(samples, part_samples=True):
    """Function to define b-tagging conditions needed for event selection filters."""
    
    # Define pt thresholds
    pt_thresholds = [10, 20, 30]

    if part_samples:
        jet_attributes = jet_attributes_global + jet_attributes_part
    else:
        jet_attributes = jet_attributes_global

    # Define b-tagging conditions for medium and loose thresholds
    for btag_level, btag_value in btag_thresholds.items():
        # Base b-tagging condition
        samples = samples.Define(f"btagged_{btag_level}_jets", f"selected_jets_pt[selected_jets_deepflavB > {btag_value}]")
        
        # Add pt thresholds - these are needed for selection filters
        for pt in pt_thresholds:
            samples = samples.Define(
                f"btagged_{btag_level}_jets_pt_above_{pt}",
                f"selected_jets_pt[selected_jets_deepflavB > {btag_value} & selected_jets_pt > {pt}]"
            )

    '''Define the btagged jets but with the bstautau mask - base collections only'''
    # Define b-tagging conditions for medium and loose thresholds
    for btag_level, btag_value in btag_thresholds.items():
        # Base b-tagging condition for histograms
        for attr in jet_attributes:
            samples = samples.Define(f"btagged_{btag_level}_jets_for_histo_{attr}", f"selected_jets_for_histo_{attr}[selected_jets_for_histo_deepflavB > {btag_value}]")

    return samples

def define_jets_with_btagging_selection_for_histos(samples, part_samples, plot_all_jets=False):
    """Function to define b-tagging histogram branches - call after snapshots."""
    
    # Define pt thresholds
    pt_thresholds = [10, 20, 30]

    if part_samples:
        jet_attributes = jet_attributes_global + jet_attributes_part
    else:
        jet_attributes = jet_attributes_global

    # Define b-tagging conditions for medium and loose thresholds
    for btag_level, btag_value in btag_thresholds.items():
        # Add pt thresholds - conditionally apply top N selection
        for pt in pt_thresholds:
            for attr in jet_attributes:
                # First create the filtered collection
                filtered_attr = f"btagged_{btag_level}_jets_pt_above_{pt}_filtered_{attr}"
                samples = samples.Define(
                    filtered_attr,
                    f"selected_jets_for_histo_{attr}[selected_jets_for_histo_deepflavB > {btag_value} & selected_jets_for_histo_pt > {pt}]"
                )
                # Choose between top 2 jets or all jets based on flag
                if plot_all_jets:
                    # Use all jets - just alias the filtered collection
                    samples = samples.Define(
                        f"btagged_{btag_level}_jets_pt_above_{pt}_for_histo_{attr}",
                        filtered_attr
                    )
                else:
                    # Take top 2 jets (current behavior)
                    if attr == 'pt':
                        samples = samples.Define(
                            f"btagged_{btag_level}_jets_pt_above_{pt}_for_histo_{attr}",
                            f"takeTopNByPt({filtered_attr}, {filtered_attr}, 2)"
                        )
                    else:
                        filtered_pt = f"btagged_{btag_level}_jets_pt_above_{pt}_filtered_pt"
                        samples = samples.Define(
                            f"btagged_{btag_level}_jets_pt_above_{pt}_for_histo_{attr}",
                            f"takeTopNByPt({filtered_attr}, {filtered_pt}, 2)"
                        )


        # Define the number of b-tagged jets for each threshold
        for pt in pt_thresholds:
            samples = samples.Define(
                f"btagged_{btag_level}_jets_pt_above_{pt}_for_histo_njets",
                f"btagged_{btag_level}_jets_pt_above_{pt}_for_histo_pt.size()"
            )

    return samples

# Keep the old function for backward compatibility, but mark it as deprecated
def define_jets_with_btagging_selection(samples, part_samples, plot_all_jets=False):
    """DEPRECATED: Use define_jets_with_btagging_selection_for_filters and define_jets_with_btagging_selection_for_histos instead."""
    samples = define_jets_with_btagging_selection_for_filters(samples, part_samples)
    samples = define_jets_with_btagging_selection_for_histos(samples, part_samples, plot_all_jets)
    return samples

def define_btagging_conditions(samples, ch):
    """Define b-tagging conditions for different channels."""
    btagging_conditions = {
        "emu"   : "btagged_loose_jets_pt_above_20.size()>=2",
        "mumu"  : "btagged_loose_jets_pt_above_20.size()>=2",
        "ee"    : "btagged_loose_jets_pt_above_20.size()>=2",
        "mu"    : "btagged_medium_jets_pt_above_20.size()>=2",
        "e"     : "btagged_loose_jets_pt_above_30.size()>=2"
    }
    
    for channel, condition in btagging_conditions.items():
        samples = samples.Define(f"btagging_condition_{channel}", condition)
    
    return samples


def define_jet_conditions(samples, ch, minimum_jet_conditions):
    """Define jet selection conditions for different channels."""
    jet_conditions = {
        "emu": f"ROOT::VecOps::Any({minimum_jet_conditions}) & (selected_jets_pt.size()>=2)",
        "mumu": f"ROOT::VecOps::Any({minimum_jet_conditions}) & (selected_jets_pt.size()>=2)",
        "ee": f"ROOT::VecOps::Any({minimum_jet_conditions}) & (selected_jets_pt.size()>=2)",
        "mu": f"ROOT::VecOps::Any({minimum_jet_conditions}) & (selected_jets_pt.size()>=4)",
        "e": f"ROOT::VecOps::Any({minimum_jet_conditions}) & (selected_jets_pt.size()>=4)"
    }
    for channel, condition in jet_conditions.items():
        samples = samples.Define(f"jet_conditions_{channel}", condition)
    
    return samples


def load_invmass():
    ##### invariant mass function
    ROOT.gInterpreter.Declare("""
    double compute_inv_mass(double pt1, double eta1, double phi1, double mass1,
    double pt2, double eta2, double phi2, double mass2) {
    TLorentzVector v1, v2;
    v1.SetPtEtaPhiM(pt1, eta1, phi1, mass1);
    v2.SetPtEtaPhiM(pt2, eta2, phi2, mass2);
    return (v1 + v2).M();
    }
    """)

    ## define MT (transverse mass)
    ROOT.gInterpreter.Declare("""
    double compute_mt(double pt, double phi, double met, double met_phi) {
    return sqrt(2 * pt * met * (1 - cos(phi - met_phi)));
    }
    """)

def load_sorting_functions():
    # Add helper function to sort and take top N jets by pT
    ROOT.gInterpreter.Declare("""
    template<typename T>
    ROOT::VecOps::RVec<T> takeTopNByPt(const ROOT::VecOps::RVec<T>& values, 
                                       const ROOT::VecOps::RVec<float>& pts, 
                                       int n = 2) {
        auto indices = ROOT::VecOps::Argsort(pts, [](float a, float b) { return a > b; });
        ROOT::VecOps::RVec<T> result;
        for (int i = 0; i < std::min(n, (int)indices.size()); i++) {
            //std::cout<< "Taking jet with pt: " << pts[indices[i]] << std::endl;                  
            result.push_back(values[indices[i]]);
        }
        return result;
    }
    """)


def define_invariant_mass_and_mt(samples,ch):
    """
    Defines the invariant mass and transverse mass (MT) for different channels.

    Parameters:
    - samples: The dictionary containing the sample data.
    - ch: The channel type (e.g., 'mumu', 'emu', 'ee', etc.).
    - k: The key in the sample dictionary.

    Returns:
    - Updated samples dictionary.
    """

    # Define the HT (sum of selected jets pt)
    #samples = samples.Define("selected_jets_ht", "Sum(selected_jets_pt)")

    # Invariant mass and MT definitions based on channel
    if ch == 'mumu':
        samples = samples.Define("inv_mass", "compute_inv_mass(mu1_pt, mu1_eta, mu1_phi, 0.105, mu2_pt, mu2_eta, mu2_phi, 0.105)")
        samples = samples.Define("MT_mu1_MET", "compute_mt(mu1_pt, mu1_phi, PuppiMET_pt, PuppiMET_phi)")
        samples = samples.Define("MT_mu2_MET", "compute_mt(mu2_pt, mu2_phi, PuppiMET_pt, PuppiMET_phi)")

    elif ch == 'emu':
        samples = samples.Define("inv_mass", "compute_inv_mass(mu1_pt, mu1_eta, mu1_phi, 0.105, e1_pt, e1_eta, e1_phi, 0.000511)")
        samples = samples.Define("MT_mu1_MET", "compute_mt(mu1_pt, mu1_phi, PuppiMET_pt, PuppiMET_phi)")
        samples = samples.Define("MT_e1_MET", "compute_mt(e1_pt, e1_phi, PuppiMET_pt, PuppiMET_phi)")

    elif ch == 'ee':
        samples = samples.Define("inv_mass", "compute_inv_mass(e1_pt, e1_eta, e1_phi, 0.000511, e2_pt, e2_eta, e2_phi, 0.000511)")
        samples = samples.Define("MT_e1_MET", "compute_mt(e1_pt, e1_phi, PuppiMET_pt, PuppiMET_phi)")
        samples = samples.Define("MT_e2_MET", "compute_mt(e2_pt, e2_phi, PuppiMET_pt, PuppiMET_phi)")

    elif ch == 'mu':
        samples = samples.Define("MT_mu1_MET", "compute_mt(mu1_pt, mu1_phi, PuppiMET_pt, PuppiMET_phi)")

    elif ch == 'e':
        samples = samples.Define("MT_e1_MET", "compute_mt(e1_pt, e1_phi, PuppiMET_pt, PuppiMET_phi)")

    return samples


def build_weight_string(k, files_names, options):
    """
    Constructs a weight expression string based on sample name and options.

    Args:
        k (str): Sample key.
        files_names (dict): Mapping of sample keys to filenames.
        options (dict): Dict of flags like compute_sfs, use_ntuples_with_sfs, etc.

    Returns:
        str: Weight expression (e.g., "norm_weight*L1PreFiringWeight_Nom*puWeight*tot_sf_weight").
    """
    weight_terms = ['norm_weight', 'L1PreFiringWeight_Nom', 'puWeight',]

    print(f"[{k}] Applying top pT reweighting")
    weight_terms.append('top_pt_weight')

    if options.compute_sfs or options.use_ntuples_with_sfs:
        print(f"[{k}] Applying scale factors")
        weight_terms.append('tot_sf_weight')

        #if 'TTT' in files_names.get(k, '') or 'BsToTauTau' in files_names.get(k, ''):

    elif options.compute_btag_sfs or options.use_ntuples_with_btag_sfs:
        print(f"[{k}] Applying SFs and btag scale factors")
        weight_terms.extend(['tot_sf_weight', 'btag_event_weight']) #both SF and btagging SFs are applied

    return '*'.join(weight_terms)