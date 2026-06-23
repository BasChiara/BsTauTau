

# input files up to date with https://cms-analysis-corrections.docs.cern.ch/#2018-ul-v9 (June 2026)

object_sfs ={
    '2017' : {},
    '2018' : {
        'muon' : {
            'file' : '/cvmfs/cms-griddata.cern.ch/cat/metadata/MUO/Run2-2018-UL-NanoAODv9/latest/muon_Z.json.gz',
            'id'   : 'NUM_TightID_DEN_genTracks',
            'iso'  : 'NUM_TightRelIso_DEN_TightIDandIPCut',
            'trg'  : 'NUM_IsoMu24_DEN_CutBasedIdTight_and_PFIsoTight',
        },
        'electron' : {
            'file' : '/cvmfs/cms-griddata.cern.ch/cat/metadata/EGM/Run2-2018-UL-NanoAODv9/latest/electron.json.gz',
            'all'  : 'UL-Electron-ID-SF',
        },
        'dileptrg' : {
            'file' : './sf_toolkit/dilepton_trigger_sfs_2018.root',
            'hname': 'h2D_SF_{channel}_lepABpt_FullError'
        },
        'eletrg'   : {
            'file'  : './sf_toolkit/electron_trigger_"+year+".root',
            'hname' : 'EGamma_SF2D'
        },
        'btag' : {
            'file'   : '/cvmfs/cms-griddata.cern.ch/cat/metadata/BTV/Run2-2018-UL-NanoAODv9/latest/btagging.json.gz',
            'mujets' : 'deepJet_mujets',
            'incl'   : 'deepJet_incl',
        },
    }
}