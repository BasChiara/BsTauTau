
from . import sf_inputs
from . import sf_utils
import correctionlib
import numpy as np
#correctionlib.register_pyroot_binding()


def compute_obj_sf(tree, channel, year):

    new_branches = {}

    # ---- MUON ----
    cfg_mu          = sf_inputs.object_sfs[year].get('muon', {})
    cset_mu         = correctionlib.CorrectionSet.from_file(cfg_mu.get('file', None))
    
    cset_muid   = cset_mu[cfg_mu.get('id', None)]
    cset_muiso  = cset_mu[cfg_mu.get('iso', None)]
    
    if channel in ['emu', 'mumu', 'mu']:

        data_mu1 = tree.arrays(["mu1_pt", "mu1_eta"], library="np")
        
        # ID
        new_branches["mu1_idsf"]       = cset_muid.evaluate(np.abs(data_mu1['mu1_eta']), data_mu1['mu1_pt'], "nominal")
        new_branches["mu1_idsfUp"]     = cset_muid.evaluate(np.abs(data_mu1['mu1_eta']), data_mu1['mu1_pt'], "systup")
        new_branches["mu1_idsfDown"]   = cset_muid.evaluate(np.abs(data_mu1['mu1_eta']), data_mu1['mu1_pt'], "systdown")
        
        #ISO
        new_branches["mu1_isosf"]      = cset_muiso.evaluate(np.abs(data_mu1['mu1_eta']), data_mu1['mu1_pt'], "nominal")
        new_branches["mu1_isosfUp"]    = cset_muiso.evaluate(np.abs(data_mu1['mu1_eta']), data_mu1['mu1_pt'], "systup")
        new_branches["mu1_isosfDown"]  = cset_muiso.evaluate(np.abs(data_mu1['mu1_eta']), data_mu1['mu1_pt'], "systdown")
        
        if channel != 'mumu' :
            new_branches    =   sf_utils.combine_insert_weight(new_branches, "mu_sf_weight", ["mu1_idsf", "mu1_isosf"])
        
        else: # second muon
            data_mu2 = tree.arrays(["mu2_pt", "mu2_eta"], library="np")
            
            # ID
            new_branches["mu2_idsf"]       = cset_muid.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "nominal")
            new_branches["mu2_idsfUp"]     = cset_muid.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "systup")
            new_branches["mu2_idsfDown"]   = cset_muid.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "systdown")

            # ISO
            new_branches["mu2_isosf"]      = cset_muiso.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "nominal")
            new_branches["mu2_isosfUp"]    = cset_muiso.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "systup")
            new_branches["mu2_isosfDown"]  = cset_muiso.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "systdown")

            new_branches    =   sf_utils.combine_insert_weight(new_branches, "mu_sf_weight", ["mu1_idsf", "mu1_isosf", "mu2_idsf", "mu2_isosf"])

    # ---- ELECTRON ----
    cfg_ele         = sf_inputs.object_sfs[year].get('electron', {})
    cset_ele        = correctionlib.CorrectionSet.from_file(cfg_ele.get('file', None))

    cset_eleall     = cset_ele[cfg_ele.get('all', None)]

    if channel in ['emu', 'ee', 'e']:

        data_e1 =  tree.arrays(["e1_pt", "e1_eta"], library="np")

        # Reco
        new_branches['e1_recosf']           = cset_eleall.evaluate(year, "sf", "RecoAbove20",     data_e1['e1_eta'], data_e1['e1_pt'])
        new_branches['e1_recosfUp']         = cset_eleall.evaluate(year, "sfup", "RecoAbove20",   data_e1['e1_eta'], data_e1['e1_pt'])
        new_branches['e1_recosfDown']       = cset_eleall.evaluate(year, "sfdown", "RecoAbove20", data_e1['e1_eta'], data_e1['e1_pt'])

        # ID
        new_branches['e1_idsf']             = cset_eleall.evaluate(year, "sf", "Tight",     data_e1['e1_eta'], data_e1['e1_pt'])
        new_branches['e1_idsfUp']           = cset_eleall.evaluate(year, "sfup", "Tight",   data_e1['e1_eta'], data_e1['e1_pt'])
        new_branches['e1_idsfDown']         = cset_eleall.evaluate(year, "sfdown", "Tight", data_e1['e1_eta'], data_e1['e1_pt'])

        if channel != 'ee':
            new_branches    =   sf_utils.combine_insert_weight(new_branches, "e_sf_weight", ["e1_recosf", "e1_idsf"])
        else : # second electron
            
            data_e2 =  tree.arrays(["e2_pt", "e2_eta"], library="np")
            
            # Reco
            new_branches['e2_recosf']           = cset_eleall.evaluate(year, "sf", "RecoAbove20",     data_e2['e2_eta'], data_e2['e2_pt'])
            new_branches['e2_recosfUp']         = cset_eleall.evaluate(year, "sfup", "RecoAbove20",   data_e2['e2_eta'], data_e2['e2_pt'])
            new_branches['e2_recosfDown']       = cset_eleall.evaluate(year, "sfdown", "RecoAbove20", data_e2['e2_eta'], data_e2['e2_pt'])

            # ID
            new_branches['e2_idsf']             = cset_eleall.evaluate(year, "sf", "Tight",     data_e2['e2_eta'], data_e2['e2_pt'])
            new_branches['e2_idsfUp']           = cset_eleall.evaluate(year, "sfup", "Tight",   data_e2['e2_eta'], data_e2['e2_pt'])
            new_branches['e2_idsfDown']         = cset_eleall.evaluate(year, "sfdown", "Tight", data_e2['e2_eta'], data_e2['e2_pt'])
            
            new_branches    =   sf_utils.combine_insert_weight(new_branches, "e_sf_weight", ["e1_recosf", "e1_idsf", "e2_recosf", "e2_idsf"])


    return new_branches


def compute_trigger_sf(tree, channel, year):

    new_branches = {}
    cfg_mu          = sf_inputs.object_sfs[year].get('muon', {})
    cfg_dileptrg    = sf_inputs.object_sfs[year].get('dileptrg', {})
    cgf_eletrg      = sf_inputs.object_sfs[year].get('eletrg', {})

    # 
    dilep_pts = {
        'mumu': ("mu1_pt", "mu2_pt"),
        'emu':  ("e1_pt",  "mu1_pt"),
        'ee':   ("e1_pt",  "e2_pt"),
    }
    
    if channel == 'mu':
        
        set_mu          = correctionlib.CorrectionSet.from_file(cfg_mu.get('file', None))
        cset_mutrg      = cset_mu[cfg_mu.get('trg', None)]
        
        data_mu = tree.arrays(["mu1_pt", "mu1_eta"], library="np")

        new_branches['trg_sf_weight']         =   cset_mutrg.evaluate(np.abs(data_mu['mu1_eta']), data_mu['mu1_pt'], "nominal")
        new_branches['trg_sf_weightUp']       =   cset_mutrg.evaluate(np.abs(data_mu['mu1_eta']), data_mu['mu1_pt'], "systup")
        new_branches['trg_sf_weightDown']     =   cset_mutrg.evaluate(np.abs(data_mu['mu1_eta']), data_mu['mu1_pt'], "systdown")

    
    elif channel in dilep_pts:

        bx, by = dilep_pts[channel]
        data = tree.arrays([bx, by], library="np") 
        
        new_branches   = sf_utils.eval_sf2Dhisto(data[bx], data[by], channel, year, cfg_dileptrg, "trg_sf_weight")
 
    elif channel == 'e':

        data = tree.arrays(["e1_pt", "e1_eta"], library="np")
        new_branches = sf_utils.eval_sf2Dhisto(data["e1_eta"], data["e1_pt"], channel, year, cgf_eletrg, "trg_sf_weight")
    
        
    return new_branches

def compute_top_pTreweight(tree, isttbar = False):

    new_branches = {}

    data = tree.arrays(["GenCand_pt", "GenCand_id"], library="ak") 
    new_branches['top_pt_weight']  = sf_utils.eval_toppt_sf(data["GenCand_pt"], data["GenCand_id"], isttbar)

    return new_branches

def compute_btag_sf(tree, channel, year, wp="L"):

    new_branches = {}

    return new_branches
