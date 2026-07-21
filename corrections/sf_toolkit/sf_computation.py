
from . import sf_inputs
from . import sf_utils
import correctionlib
import numpy as np
#correctionlib.register_pyroot_binding()

def _np(events, branches):
    """Pull flat branches from an awkward-array chunk as a dict of numpy arrays."""
    return {b: np.asarray(events[b]) for b in branches}


def buildin_sf():
    """
        Just combine weights available in nanoAOD
    """
    # PU weight
    pass



def compute_obj_sf(events, channel, year):

    new_branches = {}
    weights      = []

    # ---- MUON ----
    cfg_mu          = sf_inputs.object_sfs[year].get('muon', {})
    cset_mu         = correctionlib.CorrectionSet.from_file(cfg_mu.get('file', None))
    
    cset_muid   = cset_mu[cfg_mu.get('id', None)]
    cset_muiso  = cset_mu[cfg_mu.get('iso', None)]
    
    if channel in ['emu', 'mumu', 'mu']:

        data_mu1 = _np(events, ["mu1_pt", "mu1_eta"]) 
        
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
            weights.append("mu_sf_weight")
        
        else: # second muon
            data_mu2 = _np(events, ["mu2_pt", "mu2_eta"])
            
            # ID
            new_branches["mu2_idsf"]       = cset_muid.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "nominal")
            new_branches["mu2_idsfUp"]     = cset_muid.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "systup")
            new_branches["mu2_idsfDown"]   = cset_muid.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "systdown")

            # ISO
            new_branches["mu2_isosf"]      = cset_muiso.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "nominal")
            new_branches["mu2_isosfUp"]    = cset_muiso.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "systup")
            new_branches["mu2_isosfDown"]  = cset_muiso.evaluate(np.abs(data_mu2['mu2_eta']), data_mu2['mu2_pt'], "systdown")

            new_branches    =   sf_utils.combine_insert_weight(new_branches, "mu_sf_weight", ["mu1_idsf", "mu1_isosf", "mu2_idsf", "mu2_isosf"])
    elif channel in ['e']:
            new_branches["mu_sf_weight"]    =  np.ones(len(events), dtype=np.float64)
            weights.append("mu_sf_weight")
    
    # ---- ELECTRON ----
    cfg_ele         = sf_inputs.object_sfs[year].get('electron', {})
    cset_ele        = correctionlib.CorrectionSet.from_file(cfg_ele.get('file', None))

    cset_eleall     = cset_ele[cfg_ele.get('all', None)]

    if channel in ['emu', 'ee', 'e']:

        data_e1 =  _np(events, ["e1_pt", "e1_eta"])

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
            weights.append("e_sf_weight")
        else : # second electron
            
            data_e2 =  _np(events, ["e2_pt", "e2_eta"])
            
            # Reco
            new_branches['e2_recosf']           = cset_eleall.evaluate(year, "sf", "RecoAbove20",     data_e2['e2_eta'], data_e2['e2_pt'])
            new_branches['e2_recosfUp']         = cset_eleall.evaluate(year, "sfup", "RecoAbove20",   data_e2['e2_eta'], data_e2['e2_pt'])
            new_branches['e2_recosfDown']       = cset_eleall.evaluate(year, "sfdown", "RecoAbove20", data_e2['e2_eta'], data_e2['e2_pt'])

            # ID
            new_branches['e2_idsf']             = cset_eleall.evaluate(year, "sf", "Tight",     data_e2['e2_eta'], data_e2['e2_pt'])
            new_branches['e2_idsfUp']           = cset_eleall.evaluate(year, "sfup", "Tight",   data_e2['e2_eta'], data_e2['e2_pt'])
            new_branches['e2_idsfDown']         = cset_eleall.evaluate(year, "sfdown", "Tight", data_e2['e2_eta'], data_e2['e2_pt'])
            
            new_branches    =   sf_utils.combine_insert_weight(new_branches, "e_sf_weight", ["e1_recosf", "e1_idsf", "e2_recosf", "e2_idsf"])
            weights.append("e_sf_weight")
    
    elif channel in ['mu']:
            new_branches["e_sf_weight"]    =  np.ones(len(events), dtype=np.float64)
            weights.append("e_sf_weight")

    return new_branches, weights


def compute_trigger_sf(events, channel, year):

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
        
        cset_mu          = correctionlib.CorrectionSet.from_file(cfg_mu.get('file', None))
        cset_mutrg       = cset_mu[cfg_mu.get('trg', None)]
        
        data_mu = _np(events, ["mu1_pt", "mu1_eta"])

        new_branches['trg_sf_weight']         =   cset_mutrg.evaluate(np.abs(data_mu['mu1_eta']), data_mu['mu1_pt'], "nominal")
        new_branches['trg_sf_weightUp']       =   cset_mutrg.evaluate(np.abs(data_mu['mu1_eta']), data_mu['mu1_pt'], "systup")
        new_branches['trg_sf_weightDown']     =   cset_mutrg.evaluate(np.abs(data_mu['mu1_eta']), data_mu['mu1_pt'], "systdown")

    
    elif channel in dilep_pts:

        bx, by = dilep_pts[channel]
        data = _np(events, [bx, by])
        
        new_branches   = sf_utils.eval_sf2Dhisto(data[bx], data[by], channel, year, cfg_dileptrg, "trg_sf_weight")
 
    elif channel == 'e':

        data = _np(events, ["e1_pt", "e1_eta"])
        new_branches['trg_sf_weight'] = np.ones(len(events), dtype=np.float64) #new_branches =sf_utils.eval_sf2Dhisto(data["e1_eta"], data["e1_pt"], channel, year, cgf_eletrg, "trg_sf_weight") #FIXME missing input
    
        
    return new_branches

def compute_top_pTreweight(events, isttbar = False):

    new_branches = {}
    # FIXME: add GenCand_status to take the initial top
    new_branches['top_pt_weight']  = sf_utils.eval_toppt_sf(events["GenCand_pt"], events["GenCand_id"], isttbar)

    return new_branches

def compute_btag_sf(events, channel, year, jetbranch = "selected_jets_for_histo", wp="L", wp_val = 0.0499):

    new_branches = {}
    # up/down variations
    name_systematics = list(zip(
        ["",        "Up", "Down", "_corrUp",       "_corrDown",       "_uncorrUp",       "_uncorrDown"],
        ["central", "up", "down", "up_correlated", "down_correlated", "up_uncorrelated", "down_uncorrelated"]
    ))
    
    # jet
    jet_pt      = events[jetbranch+'_pt']
    jet_eta     = events[jetbranch+'_eta']
    jet_flav    = events[jetbranch+'_hadronFlavour']
    jet_discr   = events[jetbranch+'_deepflavB']
    
    #  retrive SF .json
    cfg_btag            = sf_inputs.object_sfs[year].get('btag', {})
    cset_btag           = correctionlib.CorrectionSet.from_file(cfg_btag.get('file', None))
    cset_btag_mujets    = cset_btag['deepJet_mujets']
    cset_btag_incl      = cset_btag['deepJet_incl']

    # split by true flavor
    is_bcj      = (jet_flav != 0 )
    is_lightj   = (jet_flav == 0 )
    bcj_sfs, lightj_sfs = {}, {}
    
    for sys_suffix, syst in name_systematics:
        bcj_sfs['btag_sf_bcjets'+sys_suffix]        = sf_utils.eval_btag(cset_btag_mujets, syst, wp, jet_flav, jet_eta, jet_pt, is_bcj)
        lightj_sfs['btag_sf_ljets'+sys_suffix]      = sf_utils.eval_btag(cset_btag_incl,   syst, wp, jet_flav, jet_eta, jet_pt, is_lightj)
    
    # merge into event-weight
    new_branches['btag_sf'] = sf_utils.eval_event_btag( # nominal
            jet_discr, wp, wp_val, 
            bcj_sfs['btag_sf_bcjets'], lightj_sfs['btag_sf_ljets'],
            jet_flav, jet_eta, jet_pt,
            cfg_btag
        )
    for sys_suffix, _ in name_systematics: # bc and light-sf variation
       if sys_suffix == "" : continue
       new_branches['btag_sf_bc'+sys_suffix] = sf_utils.eval_event_btag( # bc SF variations
            jet_discr, wp, wp_val, 
            bcj_sfs['btag_sf_bcjets'+sys_suffix], lightj_sfs['btag_sf_ljets'],
            jet_flav, jet_eta, jet_pt,
            cfg_btag
        )
       new_branches['btag_sf_l'+sys_suffix] = sf_utils.eval_event_btag( # light SF variations
            jet_discr, wp, wp_val, 
            bcj_sfs['btag_sf_bcjets'], lightj_sfs['btag_sf_ljets'+sys_suffix],
            jet_flav, jet_eta, jet_pt,
            cfg_btag
        )
    
    return new_branches
