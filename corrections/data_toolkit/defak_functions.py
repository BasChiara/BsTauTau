import awkward as ak
import numpy as np

def awfindIndicesOfBsTauTau(is_bstt_flag):
    """
    Return per-event local indices of GenCand entries where flag == 1.

    Parameters
    ----------
    is_bstt_flag : ak.Array [n_events, n_gencands]  e.g. df['GenCand_isBsTauTaunew']

    Returns
    -------
    ak.Array of int [n_events, n_signal_bs]
    """
    return ak.local_index(is_bstt_flag)[is_bstt_flag == 1]


def awmatchSignalBsToJets(bs_indices, gen_eta, gen_phi,
                        jet_pt, jet_eta, jet_phi, jet_btag,
                        btag_wp, max_dr=0.4, min_jet_pt=20.0, max_jet_eta=2.5):
    """
    Match signal Bs mesons to the nearest b-tagged jet within a dR cone.

    Parameters
    ----------
    bs_indices           : ak.Array [n_events, n_bs]      from findIndicesOfBsTauTau
    gen_eta, gen_phi     : ak.Array [n_events, n_gencands]
    jet_pt/eta/phi/btag  : ak.Array [n_events, n_jets]
    btag_wp              : float   b-tagging WP threshold
    max_dr               : float   cone size (default 0.4)
    min_jet_pt           : float   minimum jet pT in GeV (default 20)
    max_jet_eta          : float   maximum |eta| (default 2.5)

    Returns
    -------
    mask         : ak.Array of int32   [n_events, n_jets]  — 1 if matched to a signal Bs, 0 otherwise
    jet_match_dr : ak.Array of float32 [n_events, n_jets]  — dR to matched Bs, -1 if not matched
    """
    bs_eta = gen_eta[bs_indices]   # [n_events, n_bs]
    bs_phi = gen_phi[bs_indices]
    
    all_jet_idx = ak.local_index(jet_pt)
    good_jets  = (jet_pt > min_jet_pt) & (np.abs(jet_eta) < max_jet_eta) & (jet_btag > btag_wp)
    j_eta      = jet_eta[good_jets]
    j_phi      = jet_phi[good_jets]
    j_orig_idx = ak.local_index(jet_eta)[good_jets]  # preserve original indices

    # All (Bs, good-jet) pairs per event → [n_events, n_bs, n_good_jets]
    pairs = ak.cartesian(
        {"bs":  ak.zip({"eta": bs_eta, "phi": bs_phi}),
         "jet": ak.zip({"eta": j_eta,  "phi": j_phi, "orig_idx": j_orig_idx})},
        nested=True,
    )

    deta = pairs["bs"]["eta"] - pairs["jet"]["eta"]
    dphi = np.abs(pairs["bs"]["phi"] - pairs["jet"]["phi"])
    dphi = ak.where(dphi > np.pi, 2 * np.pi - dphi, dphi)
    dr   = np.sqrt(deta**2 + dphi**2)

    best_local      = ak.fill_none(ak.argmin(dr, axis=-1, keepdims=True), 0 )      # [events, n_bs, 1] (avoid empty arrays)
    best_dr         = ak.fill_none(ak.min(dr, axis=-1), 999.)                      # [events, n_bs]
    best_orig       = ak.flatten(pairs["jet"]["orig_idx"][best_local], axis=-1)    # [events, n_bs]

    in_cone         = best_dr < max_dr
    matched_jet_idx = best_orig[in_cone]                                           # [events, n_matched]
    matched_jet_dr  = best_dr[in_cone]                                             # [events, n_matched]

    # per-jet mask and dR: [n_events, n_jets, n_matched] cartesian product
    pairs = ak.cartesian(
        {"jet": all_jet_idx,
         "matched": ak.zip({"idx": matched_jet_idx, "dr": matched_jet_dr})},
        nested=True,
    )
    
    is_match     = pairs["jet"] == pairs["matched"]["idx"]                         # [events, n_jets, n_matched]
    mask         = ak.values_astype(ak.any(is_match, axis=-1), np.int32)
    min_match_dr = ak.fill_none(ak.min(ak.where(is_match, pairs["matched"]["dr"], 999.), axis=-1), 999.)
    jet_match_dr = ak.values_astype(ak.where(ak.any(is_match, axis=-1), min_match_dr, -1.), np.float32)
    
    return mask, jet_match_dr