import numpy as np
import awkward as ak
import ROOT


#def define_total_weight(sample, k, files_names, options):
#    """
#    Defines the total event weight for a given sample.
#
#    Args:
#        sample: The RDataFrame containing the sample data.
#        k (str): Sample key.
#        files_names (dict): Mapping of sample keys to filenames.
#        options (dict): Dict of flags like compute_sfs, use_ntuples_with_sfs, etc.
#
#    Returns:
#        Updated RDataFrame with a new column 'total_weight'.
#    """
#    weight_list = build_weight_string(k, files_names, options).split('*')
#    sample      = sf_cpp.combine_insert_weight(sample, 'tot_weight', weight_list, make_variations=True, debug=True)
#
#    return sample

def combine_insert_weight(
    data, 
    w_name,
    sf_branches,
    nominal_only = False,
    verbose = False
):
    """
    Define :
        w_name -> nominal weight, combination of all the SFs in sf_branches
        w_nameUp ->  w_name + w_nameUnc
        w_nameDown -> w_name - w_nameUnc

    in sample, assuming independent uncertainties, and that the variations are symmetric.
    """
    if not sf_branches:
        raise ValueError("combine_insert_weight: sf_branches is empty")

    up_t, down_t = "{}Up", "{}Down"

    # check branches
    missing = [b for b in sf_branches if b not in data]
    if missing:
        raise KeyError(f"missing nominal SF branches: {missing}")
    if not nominal_only:
        missing_var = [
            v for b in sf_branches
            for v in (up_t.format(b), down_t.format(b))
            if v not in data
        ]
        if missing_var:
            raise KeyError(f"missing variation branches: {missing_var}")

    # setup weights 
    weight = np.asarray(data[sf_branches[0]], dtype=np.float64).copy() # important copy()
    if not nominal_only:
        upvar   = np.asarray(data[up_t.format(sf_branches[0])],   dtype=np.float64).copy()
        downvar = np.asarray(data[down_t.format(sf_branches[0])], dtype=np.float64).copy()
    
    # combine
    for branch in sf_branches[1:]:
        weight  *= np.asarray(data[branch], dtype=np.float64)
        if not nominal_only:
            upvar   *= np.asarray(data[up_t.format(branch)],   dtype=np.float64)
            downvar *= np.asarray(data[down_t.format(branch)], dtype=np.float64)
    # insert
    data[w_name] = weight
    if not nominal_only:
        data[up_t.format(w_name)]   = upvar
        data[down_t.format(w_name)] = downvar
    
    if verbose:
        print(f"[combine_insert_weight] {w_name} from {sf_branches}; "
              f"mean={weight.mean():.6f}, n={weight.size}")

    return data

# lepton trigger SFs
def load_histo(filename, histoname):

    outfile  = None
    outhisto = None

    outfile = ROOT.TFile.Open(filename, "READ")
    if (not outfile) or (not outfile.IsOpen()):
        print(f"[ERROR] file {filename} NOT FOUND")
        return None
    
    outhisto = outfile.Get(histoname).Clone()
    outhisto.SetDirectory(0)
    
    if not outhisto:
        print(f"[ERROR] file {filename} NOT FOUND")
        return None


    return outhisto


def eval_sf2Dhisto(X, Y, channel, year, cfg, wname = "trg_sf_weight"):

    sf_branches = {}
    sf      = np.ones(len(X), dtype=np.float64)
    unc     = np.zeros(len(X), dtype=np.float64)
    sfup    = np.ones(len(X), dtype=np.float64)
    sfdown  = np.ones(len(X), dtype=np.float64) 

    fname = cfg.get('file', None)
    histo_tmpl = cfg.get('hname', None)

    MAX_leppT = 499.99
    sf_histo = load_histo(fname, histo_tmpl.format(channel=channel))
    for i, vv in enumerate(zip(X, Y)):
        ibinX   = sf_histo.GetXaxis().FindBin(min(vv[0], MAX_leppT)) 
        ibinY   = sf_histo.GetYaxis().FindBin(min(vv[1], MAX_leppT))

        sf[i]   = sf_histo.GetBinContent(ibinX, ibinY)
        unc[i]  = sf_histo.GetBinError(ibinX, ibinY)
    
    sfup = sf + unc
    sfdown = sf - unc

    sf_branches = {
        wname : sf,
        wname+'Up' : sfup,
        wname+'Down' : sfdown,
    }  
    
    return sf_branches


# top-pT re-weight
def top_pt_weight(pt):
    return np.exp(0.0615 - 0.0005 * pt)

def eval_toppt_sf(genpt, genid, isttbar):
    #https://twiki.cern.ch/twiki/bin/viewauth/CMS/TopPtReweighting
   
    if not isttbar : return np.ones(len(genpt), dtype=np.float64)
    
    MAX_tpT = 500.
    is_top  = (genid ==  6)
    is_atop = (genid == -6)
    # FIXME: for some reason there are 2 top and 2 anti-top
    #           pick the second one for conformity but should have status flag
    top_pt  = np.minimum(ak.to_numpy(genpt[is_top][..., -1]),  MAX_tpT)
    atop_pt = np.minimum(ak.to_numpy(genpt[is_atop][..., -1]), MAX_tpT)

    return top_pt_weight(top_pt) * top_pt_weight(atop_pt)


# b-tag scale factor
def eval_btag(cset, syst, wp, flav, eta, pt, mask, abs_eta=True):
    """
        Evaluate a b-tag SF on masked jagged jets, returning a jagged SF array.
        flatten -> evaluate -> unflatten

    """

    n   = ak.num(flav[mask]) #counts per-event -> re-built structure at unflatten stage
    
    # flatten
    f   = ak.to_numpy(ak.flatten(flav[mask])).astype(np.int32)
    e   = ak.to_numpy(ak.flatten(eta[mask])).astype(np.float64)
    p   = ak.to_numpy(ak.flatten(pt[mask])).astype(np.float64)
    if abs_eta:
        e = np.abs(e)
    
    # evaluate and unflatten
    return ak.unflatten(cset.evaluate(syst, wp, f, e, p), n)

def merge_btag_sfs(flav, bc_sfs, l_sfs):
    """
    Merge per-flavor btag SFs back into one per-jet array matching `flav`'s layout.
      flav   : jagged (nevents, nJets) hadronFlavour
      bc_sfs : jagged SFs for heavy-flavour jets (flav != 0), bc-subset layout
      l_sfs  : jagged SFs for light jets (flav == 0), light-subset layout
    Returns a jagged SF array with the SAME layout as `flav`.
    """
    n = ak.num(flav)                                  # jets per event (original)
    flat_flav = ak.to_numpy(ak.flatten(flav))         # 1D, all jets in order

    sf = np.ones(len(flat_flav), dtype=np.float64)    # one slot per jet
    bc = (flat_flav != 0)
    light = ~bc

    # bc_sfs / l_sfs are jagged in their own subspace -> flatten to 1D
    sf[bc]    = ak.to_numpy(ak.flatten(bc_sfs))
    sf[light] = ak.to_numpy(ak.flatten(l_sfs))

    return ak.unflatten(sf, n)                        # re-jag to flav's layout

def load_eff2Dhisto(cfg, wp = "L"):
 
    histfile        =  cfg.get('eff', None)
    histname_tmpl   =  cfg.get('effname', None)
    eff_hist_b  =  load_histo(histfile, histname_tmpl.format(workingpoint=wp, jetflavor='b'))
    eff_hist_c  =  load_histo(histfile, histname_tmpl.format(workingpoint=wp, jetflavor='c'))
    eff_hist_l  =  load_histo(histfile, histname_tmpl.format(workingpoint=wp, jetflavor='udsg'))
    
    if (not eff_hist_b) or (not eff_hist_c) or (not eff_hist_l) :
        print(f"ERROR: b-tag efficiency histos for {wp} working point NOT FOUND.")
        return None, None, None
    
    return eff_hist_b, eff_hist_c, eff_hist_l

def eval_btag_efficiency(f_flav, f_eta, f_pt, wp, cfg):
    """
    b-tagging efficiency from histogram based on flat input
    """

    # get efficiency histograms by flavor
    heff_b, heff_c, heff_light = load_eff2Dhisto(cfg, wp)
    if (not heff_b) or (not heff_c) or (not heff_light) :
        print(f"ERROR: b-tag efficiency histos for {wp} working point NOT IMPORTED.")
        return False

    # evaluate efficiency
    MAX_jpt = 1000
    clamp_pt = np.minimum(f_pt, MAX_jpt)
    
    eff  = np.ones_like(f_pt, dtype=np.float64)
    is_b = (f_flav == 5)
    is_c = (f_flav == 4)
    is_l = (f_flav == 0)

    eff[is_b] = np.array([ heff_b.GetEfficiency(heff_b.FindFixBin(x, y))         for x, y in zip(clamp_pt[is_b], np.abs(f_eta[is_b])) ], dtype=np.float64)
    eff[is_c] = np.array([ heff_c.GetEfficiency(heff_c.FindFixBin(x, y))         for x, y in zip(clamp_pt[is_c], np.abs(f_eta[is_c])) ], dtype=np.float64)
    eff[is_l] = np.array([ heff_light.GetEfficiency(heff_light.FindFixBin(x, y)) for x, y in zip(clamp_pt[is_l], np.abs(f_eta[is_l])) ], dtype=np.float64)

    return np.minimum(eff, 1.-1e-6)

def eval_event_btag(discr, wp, wp_val, bc_sfs, l_sfs, flav, eta, pt, cfg, debug =False):
    """
    Per-event btag scale factor according to BTV recomendation
    https://btv-wiki.docs.cern.ch/PerformanceCalibration/fixedWPSFRecommendations/
        tagged jet   -> SF
        untagged jet -> (1 - SF*eff) / (1 - eff)
    """
    
    # merge bc and light SFs
    sf = merge_btag_sfs(flav, bc_sfs, l_sfs)

    # separate b-tagged and weight untagged by the efficiency
    n         = ak.num(sf)                      
    sf_flat   = ak.to_numpy(ak.flatten(sf))
    tag_flat  = ak.to_numpy(ak.flatten(discr > wp_val))

    # load btag efficiency

    eff = eval_btag_efficiency(
        ak.to_numpy(ak.flatten(flav)), ak.to_numpy(ak.flatten(eta)), ak.to_numpy(ak.flatten(pt)),
        wp, cfg
    )
    
    #1e-1*np.ones_like(sf_flat) #FIXME: placeholder

    # per-jet weight
    w_flat = np.where( # get SF ((1-SF*eff)/(...)) if tag_flat = True(False)
        tag_flat,
        sf_flat,
        (1-sf_flat*eff)/(1-eff)
    )
    # re-jag and multiply over jets in each event
    w_jagged = ak.unflatten(w_flat, n)
    
    if debug:
        print(" [eval_event_btag()] - jets per event", n)
        print(" [eval_event_btag()] - SF flat", sf_flat)
        print(" [eval_event_btag()] - efficiency flat", eff)
        print(" [eval_event_btag()] - event-weight flat", w_flat) 
        print(" [eval_event_btag()] - event-weight (nevents, njets)", w_jagged) 

    return ak.to_numpy(ak.prod(w_jagged, axis=1))


