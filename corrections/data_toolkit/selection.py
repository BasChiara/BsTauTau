# -- PRESELECTION --

preselection = dict()

preselection['emu']= ' & '.join([
    'max(mu1_pt,e1_pt)>25', 
    'mu1_pt>20', 
    'mu1_eta<2.4', 
    'e1_pt>20', 
    'e1_eta<2.4', 
    'PuppiMET_pt>20',
    #'inv_mass>20',
    #'!(inv_mass > 50 && inv_mass < 85)',
    'btagging_condition_emu',
    'jet_conditions_emu'
])

preselection['mumu']= ' & '.join([
    'max(mu1_pt,mu2_pt)>25', 
    'mu1_pt>20', 
    'mu1_eta<2.4', # silicon tracker threshold
    'mu2_pt>20', 
    'mu2_eta<2.4', # silicon tracker threshold
    'PuppiMET_pt>20',
    'inv_mass>20',
    '!(inv_mass > 76.2 && inv_mass < 106.2)',
    'btagging_condition_mumu',
    'jet_conditions_mumu',
    'MT_mu1_MET>50',
    'MT_mu2_MET>50'
])

preselection['ee']= ' & '.join([
    'max(e1_pt,e2_pt)>25',
    'e1_pt>20', 
    'e1_eta<2.4', # silicon tracker threshold
    'e2_pt>20', 
    'e2_eta<2.4', # silicon tracker threshold
    'PuppiMET_pt>20',
    'inv_mass>20',
    '!(inv_mass > 76.2 && inv_mass < 106.2)',
    'btagging_condition_ee',
    'jet_conditions_ee',
    'MT_e1_MET>50',
    'MT_e2_MET>50'
])

preselection['e']= ' & '.join([
    'e1_pt>34', 
    'e1_eta<2.4', # silicon tracker threshold
    'btagging_condition_e',
    'jet_conditions_e',
    'PuppiMET_pt>20',
    #'MT_e1_MET>50'
])

preselection['mu']= ' & '.join([
    'mu1_pt>30', # > 27 GeV trigger threshold
    'mu1_eta<2.4', # silicon tracker threshold
    'btagging_condition_mu',
    'jet_conditions_mu',
    'PuppiMET_pt>20',
    #'MT_mu1_MET>50'
])



# -- TRIGGER --
# Define trigger selections and exclusions for each data sample
trigger_selections = {
    'mu':{
        'data_sm': 'HLT_IsoMu24',
        },
    # from https://cms.cern.ch/iCMS/analysisadmin/cadilines?id=2466&ancode=TOP-21-010&tp=an&line=TOP-21-010
    'e':{
        'data_eg': 'HLT_Ele32_WPTight_Gsf',
    },
    'mumu':{
        'data_sm': 'HLT_IsoMu24',
        'data_dm': 'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8',
    },
    'emu':{
        'data_sm': 'HLT_IsoMu24',
        'data_eg': 'HLT_Ele32_WPTight_Gsf',
        'data_meg': 'HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ | HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ | HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL'
    },
    'ee':{
        'data_eg': 'HLT_Ele32_WPTight_Gsf | HLT_DoubleEle25_CaloIdL_MW | HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL',
    }
}

trigger_exclusions = {
    'mu':{
        'data_sm': [], # nothing to be excluded here
        },
    'e':{
        'data_eg': [], # nothing to be excluded here
        },
    'emu':{
        'data_sm': [], # nothing to be excluded here
        'data_eg': ['HLT_IsoMu24'],  
        'data_meg': ['HLT_IsoMu24','HLT_Ele32_WPTight_Gsf']  
    },
    'mumu':{
        'data_sm': [], # nothing to be excluded here
        'data_dm': ['HLT_IsoMu24'], 
    },
    'ee':{
        'data_eg': [], # nothing to be excluded here
    }
}


# -- JETS --
unique_minjet_cond = '&&'.join([
    '(j_pt > 20)', # b-tagging SFs (JEC pT>10 GeV)
    '(abs(j_eta)< 2.5)',
    '(j_jetid>=2)',
])
min_jet_selection = {
    'emu'   : unique_minjet_cond,
    'mumu'  : unique_minjet_cond,
    'ee'    : unique_minjet_cond,
    'e'     : unique_minjet_cond,
    'mu'    : unique_minjet_cond
}

# --- SIGNAL BsTauTau ---
bstautau_conditions = {
    "general":      "SigJetMask",
    "tauhtauh":     "SigJetMaskTauhtauh",
    "tauhtaue":     "SigJetMaskTauhtaue",
    "tauhtaumu":    "SigJetMaskTauhtaumu"
}

# --- BTAG working point ---
btag_wpval  = { #FIXME :check - https://btv-wiki.docs.cern.ch/ScaleFactors/Run2UL2018NanoAODv9/
    'L' : 0.0499,
    'M' : 0.2770,
}
btag_chwp   = {
    'emu'   : ('L',btag_wpval['L']),
    'ee'    : ('L',btag_wpval['L']),
    'mmu'   : ('L',btag_wpval['L']),
    'e'     : ('L',btag_wpval['L']),
    'mu'    : ('M',btag_wpval['M']),
}