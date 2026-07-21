import CRABClient
from CRABClient.UserUtilities import config, ClientException
import yaml
import datetime
from fnmatch import fnmatch
import argparse

import os, sys

from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from http.client import HTTPException
def submit(config, dryrun = False):
      try:
          print(config)
          if not dryrun: crabCommand('submit', config = config)
      except HTTPException as hte:
          print("Failed submitting task:",hte.headers)
      except ClientException as cle:
          print("Failed submitting task:",cle)

if __name__ == '__main__':
    
    #from multiprocessing import Process

    
    # default input arguments
    defaults_ = {
        'filter'        : '*',
        'config'        : 'run_nanoUL18_150X_cfg.py', 
        'campaign'      : 'RunIIUL18', 
        'output_dir'    : '/store/group/phys_bphys/cbasile/BsTauTau-ttbar/nanov15_UParTditau/',
        'version'       : 0,
        'MaxFiles'      : 10000,
        'tag'           : None

    }

    parser = argparse.ArgumentParser(description='CRAB configuration for BsTauTau miniAOD -> nanoAOD (+ ParT tagger) converter.')
    parser.add_argument('--dataset',
                        type=str, required=True,
                        help=".yaml file with dataset(s) informations"
                        )
    parser.add_argument('-f', '--filter', 
                        type=str, default=defaults_['filter'], 
                        help = f'filter samples, POSIX regular expressions allowed| DEFAULT  = "{defaults_["filter"]}" (all samples)')
    parser.add_argument('--config', 
                        type=str, default=defaults_['config'],
                        help=f'PSet.py file to run on grid via cmsRun| DEFAULT  = "{defaults_["config"]}"'
                        )
    #parser.add_argument('-e', '--executable', 
    #                    type=str, required=False,
    #                    help='path to the .sh file with the generation chain commands'
    #                    )
    parser.add_argument('--campaign',
                        default=defaults_['campaign'],
                        help=f'campaign for the production| DEFAULT  = "{defaults_["campaign"]}"'
                        )
    parser.add_argument('-o', '--output_dir', 
                        default = defaults_['output_dir'], 
                        help = 'output directory for the jobs - without /eos/cms prefix'
                        )
    parser.add_argument('-t', '--tag',
                        type=str, default=defaults_['tag'],
                        help=f'tag for the production| DEFAULT  = "{defaults_["tag"]}"'
                        )
    parser.add_argument('-v', '--version',
                        type=int, default=defaults_['version'],
                        help=f'version of the production| DEFAULT  = "{defaults_["version"]}"'
                        )
    parser.add_argument('-F', '--MaxFiles',
                        type=int, default=defaults_['MaxFiles'],
                        help=f'MAX number of files to process| DEFAULT  = "{defaults_["MaxFiles"]}"'
                        ) 
    #parser.add_argument('-n', '--splitperjob',
    #                    type=int, default=1000,
    #                    help=f'Files per job| DEFAULT  = "{defaults_["splitperjob"]}"'
    #                    ) 
    parser.add_argument('--dryrun',
                        action='store_true',
                        help='perform a dry run without submitting the task'
                        )
    
    
    # parse input arguments
    args = parser.parse_args()
    
    indatasets      = args.dataset
    tofilter        = args.filter
    config_file     = args.config
    #executable      = args.executable
    #process_name    = 'args.process_name'
    tag             = args.tag
    campaign        = args.campaign
    step            = 'nanoAODv15'
    todaystring     = datetime.date.today().strftime('%Y%b%d')
    version         = 'v'+str(args.version)
    unitstot        = args.MaxFiles
    #unitsjob        = args.splitperjob
    dry_run_ = args.dryrun

    # parse .yaml with dataset info
    with open(indatasets) as f:
        doc = yaml.load(f,Loader=yaml.FullLoader) # Parse YAML file
    common = doc.get('common', {'data' : {}, 'mc' : {}})
    
    # loop over samples
    # CRAB configuration
    config = config()
    for sample, info in doc['samples'].items():
        if not fnmatch(sample, tofilter): continue
        print(f" ------ {sample} ------- ")

        thiscommon = common.get('mc' if info.get('isMC', True) else 'data', {})

        process_name    = sample
        request_name    = '_'.join(filter(None, [process_name, step, tag, version]))
        work_area       = '_'.join(filter(None, ["crabjobs", version, todaystring])) 
        dataset_tag     = '_'.join(filter(None, [process_name, campaign, step, tag]))

        config.section_('General')
        config.General.requestName      = request_name
        config.General.workArea         = work_area
        config.General.transferOutputs  = True
        config.General.transferLogs     = True

        config.section_('Data')
        config.Data.inputDataset         = info.get('dataset', None)
        config.Data.publication          = False
        config.Data.outLFNDirBase        = os.path.join(args.output_dir, config.General.workArea)  
        config.Data.outputDatasetTag     = dataset_tag
        config.Data.splitting            = 'FileBased'
        config.Data.unitsPerJob          = info.get('splitting', thiscommon.get('splitting', 10))
        config.Data.totalUnits           = unitstot
        config.Data.outputDatasetTag     = dataset_tag
        config.Data.inputDBS             = 'global' #'phys03'


        config.section_('JobType')
        config.JobType.pluginName                       = 'Analysis'
        config.JobType.psetName                         = config_file   
        config.JobType.allowUndistributedCMSSW          = True
        config.JobType.disableAutomaticOutputCollection = True
        config.JobType.outputFiles                      = ['step_nanoAODv15.root']
        config.JobType.numCores                         = 2
        config.JobType.maxMemoryMB                      = 5000 # MAX 2500*numCores
        #config.JobType.maxJobRuntimeMin                 = 2750 # ~ 46 hours (default: 1315)

        config.section_('User')

        config.section_('Site')
        config.Site.storageSite = 'T2_CH_CERN'
        config.Site.blacklist   = ['T2_BE_IIHE']
 
        # time to submit 
        submit(config, dry_run_)

