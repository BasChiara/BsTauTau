
from . import sf_inputs
import correctionlib
import numpy as np
#correctionlib.register_pyroot_binding()

def compute_obj_sf(tree, channel, year):

    new_branches = {}

    # Muon
    cfg_mu      = sf_inputs.object_sfs[year].get('muon', {})
    cset_mu     = correctionlib.CorrectionSet.from_file(cfg_mu.get('file', None))
    
    cset_muid   = cset_mu[cfg_mu.get('id', None)]
    cset_muiso  = cset_mu[cfg_mu.get('iso', None)]
    if channel in ['emu', 'mumu', 'mu']:

        data_mu1 = tree.arrays(["mu1_pt", "mu1_eta"], library="np")
        
        # ID
        new_branches["mu1_idsf"]       = cset_muid.evaluate(data_mu1['mu1_eta'], data_mu1['mu1_pt'], "nominal")
        new_branches["mu1_idsfUp"]     = cset_muid.evaluate(data_mu1['mu1_eta'], data_mu1['mu1_pt'], "systup")
        new_branches["mu1_idsfDown"]   = cset_muid.evaluate(data_mu1['mu1_eta'], data_mu1['mu1_pt'], "systdown")

        print (f"Muon ID SFs computed for {len(new_branches['mu1_idsf'])} events")
        print(new_branches['mu1_idsf'][:5])

        #ISO
        new_branches["mu1_isosf"]      = cset_muiso.evaluate(data_mu1['mu1_eta'], data_mu1['mu1_pt'], "nominal")
        new_branches["mu1_isosfUp"]    = cset_muiso.evaluate(data_mu1['mu1_eta'], data_mu1['mu1_pt'], "systup")
        new_branches["mu1_isosfDown"]  = cset_muiso.evaluate(data_mu1['mu1_eta'], data_mu1['mu1_pt'], "systdown")
        print(new_branches['mu1_isosf'][:5])
        
        if channel != 'mumu' :
            new_branches["mu_sf_weight"] = new_branches["mu1_idsf"] * new_branches["mu1_isosf"]
            print(new_branches["mu_sf_weight"][:5])
        
        else: # combine with second muon
            data_mu2 = tree.arrays(["mu2_pt", "mu2_eta"], library="np")
            
            # ID
            new_branches["mu2_idsf"]       = cset_muid.evaluate(data_mu2['mu2_eta'], data_mu2['mu2_pt'], "nominal")
            new_branches["mu2_idsfUp"]     = cset_muid.evaluate(data_mu2['mu2_eta'], data_mu2['mu2_pt'], "systup")
            new_branches["mu2_idsfDown"]   = cset_muid.evaluate(data_mu2['mu2_eta'], data_mu2['mu2_pt'], "systdown")

            new_branches["mu_sf_weight"] = new_branches["mu1_idsf"] * new_branches["mu1_isosf"] * new_branches["mu2_idsf"]

            # ISO
            new_branches["mu2_isosf"]      = cset_muiso.evaluate(data_mu2['mu2_eta'], data_mu2['mu2_pt'], "nominal")
            new_branches["mu2_isosfUp"]    = cset_muiso.evaluate(data_mu2['mu2_eta'], data_mu2['mu2_pt'], "systup")
            new_branches["mu2_isosfDown"]  = cset_muiso.evaluate(data_mu2['mu2_eta'], data_mu2['mu2_pt'], "systdown")

            new_branches["mu_sf_weight"]   = new_branches["mu1_idsf"] * new_branches["mu1_isosf"] * new_branches["mu2_idsf"] * new_branches["mu2_isosf"]


    return new_branches

def compute_btag_sf(tree, channel, year, wp="L"):

    new_branches = {}

    return new_branches
