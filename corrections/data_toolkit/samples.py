import ROOT
import yaml

# -- FUNCTIONS
def parse_inyml(infile):
    
    with open(infile, 'r') as f:
        input_data = yaml.safe_load(f)
    return input_data


# -- years of data taking
# https://twiki.cern.ch/twiki/bin/view/CMS/LumiRecommendationsRun2#Luminosity_for_pp_13_TeV_data_20

luminosity_year = { # in fb-1
    '2016' : {
        'B_ver1'    : -1,
        'B_ver2'    : -1,
        'C'         : -1,
        'D'         : -1,
        'E'         : -1,
        'total'     : 36.33,
        'relunc'    : 0.0120,
    },
    '2017' : {
        'B'         : -1,
        'C'         : -1,
        'D'         : -1,
        'E'         : -1,
        'F'         : -1,
        'total'     : 41.53,
        'relunc'    : 0.0082,
    },
    '2018' : {
        'A'         : -1,
        'B'         : -1,
        'C'         : -1,
        'D'         : -1,
        'total'     : 59.74,
        'relunc'    : 0.0084,
    },
}
years = list(luminosity_year.keys())
eras = dict()
[eras.update({year:list(luminosity_year[year].keys()).remove('total')}) for year in years]

luminosity_year['Run2'] ={'total' : luminosity_year['2016']['total'] + luminosity_year['2017']['total'] + luminosity_year['2018']['total']}

# FXME : remove
eras_2018 = ['A','B','C','D']
luminosity_2018 = 59.7 # in fb-1

# -- samples

data_samples_names = {
    'mu':['data_sm'],
    'e':['data_eg'],
    'emu': ['data_sm','data_eg','data_meg'],
    'mumu':['data_sm','data_dm'],
    'ee':['data_eg']
}
channels = list(data_samples_names.keys())

## channel-labels
ch_labels = dict(zip(channels, ["#mu", "e", "e#mu", "#mu#mu", "ee"]))

mc_samples_names = [
    'tt_fullylep',
    'tt_semilep',
    'tt_had',
    'ww',
    'wz',
    'zz',
    'st_s',
    #'st_t', # FIXME : to be re-intro
    'st_antit',
    'st_tw',
    'st_antitw',
    'w',
    'wext',
    'dy',
    'bstautau',
    #'dyext' 
]

files_names = dict()
files_names['data_sm']      = 'SingleMuon'
files_names['data_dm']      = 'DoubleMuon'
files_names['data_eg']      = 'EGamma'
files_names['data_meg']     = 'MuonEG'
files_names['tt_fullylep']  = 'TTTo2L2Nu'
files_names['tt_semilep']   = 'TTToSemileptonic'
files_names['tt_had']       = 'TTToHadronic'
files_names['w']            = 'W'
files_names['wext']         = 'W_ext'
files_names['dy']           = 'DY'
files_names['dyext']        = 'DY_ext'
files_names['ww']           = 'WW'
files_names['wz']           = 'WZ'
files_names['zz']           = 'ZZ'
files_names['st_s']         = 'ST_s'
files_names['st_t']         = 'ST_t_top'
files_names['st_antit']     = 'ST_t_antitop'
files_names['st_tw']        = 'ST_tW'
files_names['st_antitw']    = 'ST_tW_antitop'
files_names['bstautau']     = 'ttbarToBsToTauTau'



#https://twiki.cern.ch/twiki/bin/viewauth/CMS/XsdbTutorialSep#TTbar
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/SummaryTable1G25ns#Diboson
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/SummaryTable1G25ns#TTbar
#https://twiki.cern.ch/twiki/bin/viewauth/CMS/StandardModelCrossSectionsat13TeV

_xsec_ttbar     =   {# in pb (NNLO + NNLL) https://twiki.cern.ch/twiki/bin/view/LHCPhysics/TtbarNNLO
    'central' : 833.9,
    'uncertainty' : { # (+,-) +20.5 -30.0	± 21.0	-22.5 +23.2
        'scale'        : (20.5, 30.0), 
        'pdf-alphas'   : (21.0, 21.0),
        #'topmass'      : (22.5, 23.2),
        'total'        : (36.6, 36.6), # conservative approach, symmetrising the total uncertainty
    }
}
_xsec_samples  = { #(pb)
    "tt_semilep": 366.29,       # (NNLO + NNLL) 
    "tt_fullylep": 88.51,       # (NNLO + NNLL) 
    "tt_had": 378.93,           # (NNLO + NNLL) 
    "w": 61526,                 #
    "wext": 61526,              #
    "dy": 6077,                 #
    "dyext": 6077,              #
    "wz": 47.13,                #
    "ww": 115.0,                # # CHECKKK
    "zz": 16.523,               #
    "st_s": 3.36,               #
    "st_t": 44.33,              # # CHECKKK
    "st_antit": 26.38,          # # CHECKKK
    "st_tw": 35.85,             # # CHECKKK
    "st_antitw": 35.85,         # # CHECKKK
    "bstautau": _xsec_ttbar['central'] * 0.16 * 6.8 * 0.001 *10,        ## xsec(ttbar) * filter-efficiency * Br(Bs->tautau) (10 times LHCb)
}
_xsec_samples_relunc = { # for naive uncertainty propagation
    "tt_semilep"    : _xsec_ttbar['uncertainty']['total'][0]/_xsec_ttbar['central'],
    "tt_fullylep"   : _xsec_ttbar['uncertainty']['total'][0]/_xsec_ttbar['central'],
    "tt_had"        : _xsec_ttbar['uncertainty']['total'][0]/_xsec_ttbar['central'],
    "w"             : 0.0,            
    "wext"          : 0.0,         
    "dy"            : 0.0,           
    "dyext"         : 0.0,        
    "wz"            : 0.0,           
    "ww"            : 0.0,           
    "zz"            : 0.0,          
    "st_s"          : 0.0,         
    "st_t"          : 0.0,         
    "st_antit"      : 0.0,     
    "st_tw"         : 0.0,        
    "st_antitw"     : 0.0,    
    "bstautau"      : 0.0,
} 

## titles
titles = dict()
titles['data_sm'] = 'data'
titles['data_eg'] = 'data'
titles['tt_fullylep'] = 't#bar{t} lep'
titles['tt_semilep'] = 't#bar{t} semi-lep'
titles['tt_had'] = 't#bar{t} had'
titles['ww'] = 'WW'
titles['w'] = 'W+jets'
titles['dy'] = 'DY'
titles['wz'] = 'WZ'
titles['zz'] = 'ZZ'
titles['st_s'] = 'ST_s'
titles['st_t'] = 'ST_t_top'
titles['st_antit'] = 'ST_t_antitop'
titles['st_tw'] = 'ST_tW_top'
titles['st_antitw'] = 'ST_tW_antitop'
titles['bstautau'] = 'B_{s}#rightarrow #tau #tau'



## colours
colours = dict()
colours['data_sm' ] = ROOT.kBlack
colours['data_eg' ] = ROOT.kBlack
colours['data_meg' ] = ROOT.kBlack
colours['tt_fullylep' ] = ROOT.TColor.GetColor("#92dadd")
colours['tt_semilep'  ] = ROOT.TColor.GetColor("#bd1f01")
colours['tt_had' ] = ROOT.TColor.GetColor("#b9ac70")
colours['ww' ] = ROOT.TColor.GetColor("#e76300")
colours['wz'  ] = ROOT.TColor.GetColor("#717581")
colours['zz'] = ROOT.TColor.GetColor("#832db6")
colours['st_s'] = ROOT.TColor.GetColor("#94a4a2")
colours['st_t'] = ROOT.TColor.GetColor("#a96b59")
colours['st_antit'] = ROOT.TColor.GetColor("#ffa90e")
colours['st_tw'] = ROOT.TColor.GetColor("#832db6")
colours['st_antitw'] = ROOT.TColor.GetColor("#94a4a2")
colours['w'] = ROOT.TColor.GetColor("#92dadd")
colours['wext'] = ROOT.TColor.GetColor("#92dadd")
colours['dy'] = ROOT.TColor.GetColor("#e76300")
colours['dyext'] = ROOT.TColor.GetColor("#e76300")
colours['bstautau'] = ROOT.TColor.GetColor("#ffa90e")
