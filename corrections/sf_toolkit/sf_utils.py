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
    
    nevents = len(genpt)
    sf  =  np.ones(nevents, dtype=np.float64)

    if not isttbar : return sf
    
    MAX_tpT = 499.99
    is_top  = (genid ==  6)
    is_atop = (genid == -6)
    # FIXME: for some reason there are 2 top and 2 anti-top
    #           pick the second one for conformity but should have status flag
    top_pt  = np.minimum(ak.to_numpy(genpt[is_top][..., -1]),  MAX_tpT)
    atop_pt = np.minimum(ak.to_numpy(genpt[is_atop][..., -1]), MAX_tpT)

    print(atop_pt)

    return top_pt_weight(top_pt) * top_pt_weight(atop_pt)


# b-tag scale factor

