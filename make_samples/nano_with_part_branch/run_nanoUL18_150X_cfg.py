# Auto generated configuration file
# using: 
# Revision: 1.19 
# Source: /local/reps/CMSSW/CMSSW/Configuration/Applications/python/ConfigBuilder.py,v 
# with command line options: --step NANO:@BTV --eventcontent NANOAODSIM --datatier NANOAODSIM --customise Configuration/DataProcessing/Utils.addMonitoring --conditions 150X_mc2018_realistic_v1 --era Run2_2018,run2_nanoAOD_106Xv2 --python_filename run_nanobtvUL18_150X_cfg.py --fileout file:step_nanobtvAODv15.root --filein dbs:/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2/MINIAODSIM -n 10 --mc
import FWCore.ParameterSet.Config as cms

from Configuration.Eras.Era_Run2_2018_cff import Run2_2018
from Configuration.Eras.Modifier_run2_nanoAOD_106Xv2_cff import run2_nanoAOD_106Xv2

process = cms.Process('NANO',Run2_2018,run2_nanoAOD_106Xv2)

# import of standard configurations
process.load('Configuration.StandardSequences.Services_cff')
process.load('SimGeneral.HepPDTESSource.pythiapdt_cfi')
process.load('FWCore.MessageService.MessageLogger_cfi')
process.load('Configuration.EventContent.EventContent_cff')
process.load('SimGeneral.MixingModule.mixNoPU_cfi')
process.load('Configuration.StandardSequences.GeometryRecoDB_cff')
process.load('Configuration.StandardSequences.MagneticField_cff')
process.load('PhysicsTools.NanoAOD.nano_cff')
process.load('Configuration.StandardSequences.EndOfProcess_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(-1),
    output = cms.optional.untracked.allowed(cms.int32,cms.PSet)
)

# Input source
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/01B61B6C-3245-824E-874A-643BAE58C6C1.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/060C5CCE-35EB-3E4C-87A1-DFA3E9A73D8F.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/08644761-458F-6643-AA93-8F82D508FDB1.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/0902FAB3-76B3-864F-AD50-34D1F945D2DD.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/0B948241-BC54-7049-B3D8-F32C25BDDFD0.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/0F70370C-4C4C-7544-8843-0A0E9B550D5E.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/13B34BAA-81C1-D44D-BB53-5B1C17DF4402.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/15F7DC1E-A330-7541-82F2-AED084D9F4FE.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/17B6D0AE-2E41-3446-A1E8-F1BCB13677BA.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/195C2CE1-FFEE-6847-9EB8-4DE82CE972DC.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/1C27ACBB-0F1D-1543-B0F8-DC88550739AB.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/1D94A0E2-F5D5-2345-AFB8-7B08DFACCCD8.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/227AF6D8-95BE-3644-BEF5-0091B15E82CE.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/293A658F-72F4-B14B-84FE-52BE17D3FE1F.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/301FBA59-678E-474A-8D06-A39B8FC64798.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/31B4D29E-BACD-FB44-8CA1-75D3A0F164A4.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/3910BE9A-B5D9-A241-B4DC-72B292287F08.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/3BFA1253-E5FE-4C48-855B-734710E78F9F.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/3D4FA3DE-82F1-F94C-AAA8-ED06CF26A5BF.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/3D6A4472-2292-D540-97CF-D66AD016DBEA.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/3E36DE80-93C4-584B-A55F-8B248470BE2A.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/4452DC4F-5BB1-9645-97A9-277048A3BB00.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/4739CC64-9D4C-CC46-A59A-C5AD72280365.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/47F9B40E-3CCB-0F48-AE99-D3BE3F96CC61.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/4A82E795-FE1F-8D41-9CCF-93A9CB8B2DFB.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/4B0D4C9D-AF33-6646-9FDC-003EF67018B3.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/52706B4D-F494-8B41-93AE-C85F52686BBC.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/52726687-FE78-D241-8E5F-576776294A84.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/583AC6C4-EB72-F941-A699-256A06AFCBA8.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/5BA293DE-1388-8D44-9644-16D5B1F6E99F.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/5CD6A57E-E911-524E-851C-6A7513AD67FC.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/61B0A641-4E8D-2A45-A7C3-2BEA155CA81A.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/64A4A4CB-C261-9046-92CC-DC4C307A654A.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/696D0D5B-E182-804B-9DD5-4D1B35951E52.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/6C4E310E-4689-6946-915D-39F275D14066.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/763373AD-46F9-3F4F-9E0D-64090B8ED945.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/768DC5F5-9079-1847-94A8-85FCDB8EAB92.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/7C223C55-02F1-4D48-A8FC-3F870C65168D.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/7CC89EE1-B0D7-274F-9C71-63DB192C53A9.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/7D422403-E444-C748-BF6F-6598393E1C7E.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/7E2667B1-C45C-664A-B4FD-7B9C218BF3A6.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/7FEB1EB5-FB41-7748-872C-0219CF813B5E.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/8607A062-A594-3449-BC86-614CA9A148B3.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/8C1D26E6-2C90-CB4A-87D1-2CF96E190F86.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/8F58E442-5209-D94B-8006-6F9D31E4918E.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/97253B55-36C1-9A40-8083-6FAD5A7A61D7.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/9909CFE5-90FB-6545-8E8B-410630F2701F.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/9B16C197-005C-414E-92B8-D008D7A8E266.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/A0561D8D-3C19-E942-8047-9A209E071721.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/A0C95460-5612-CA4D-8C8F-499F6CA776E6.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/A16DE961-D250-E541-AAA4-5BBDBC99F118.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/A34C229F-2362-6C40-B4D5-12F0D8AA407F.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/A9D416E5-1CB2-0A42-BF08-06AD41F9BC05.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/AB9BB079-5D25-4445-9CEA-91DF5CDE3406.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/AE366EDD-C9CA-BB4E-A057-0E3B88F845B5.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/B1A3765F-7CD2-D746-A3D2-08E35FFACA6F.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/B2E66754-F25A-B64F-9EFF-C14E16A1C086.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/B55E3138-14AC-A04D-99EB-48443744CF43.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/B5688714-7A8E-3541-AB2F-C06D4993F4E9.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/B660E6C6-55C7-0041-A1C4-7E8DC966B8E4.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/B8723BB5-A8F0-7140-9E87-92E556554877.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/B96C43D9-5928-7043-82AE-9656D594F837.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/C17F9692-92F6-354A-B121-7717D9699F26.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/C1C24C29-124A-8146-A704-BA205D4D61DD.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/C2D95FC7-F756-3140-A550-F641C464B840.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/C3D43645-E59C-8540-92B1-4717DB77A157.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/CD47C8FB-EEE9-6540-93F1-E89235ED886F.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/CD4CB5CB-C9EB-7D43-A7DB-12625091A28D.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/CFDAE2BC-D4D1-1343-B8D9-A857D487EBAF.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/D0F90109-252E-554D-B4EF-E31AED7E6362.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/D57B623E-7719-DA43-9197-7708BD3BF3BD.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/D5CD6A30-56B2-3A45-B787-593FDDAE0E0E.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/DD1044AD-3693-7E48-AA08-07C68EC2A175.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/EA3F5AFC-1B0E-4A4C-963F-539B52E6F509.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/EC4721E4-2141-0F4B-82E8-36AEE994B077.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/EEF9F137-5FB6-F84C-8749-652027BAFDBB.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/F1DE8922-B17E-314E-9A25-CA5B1F30B4AA.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/F5D58907-293E-F340-82AE-CD3C415DDEB1.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/F898C7A8-B30F-2F42-80F7-D7010A86DF00.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/FA918371-E721-504E-AD87-5B0D38D4D8C6.root',
        '/store/mc/RunIISummer20UL18MiniAODv2/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/MINIAODSIM/106X_upgrade2018_realistic_v16_L1v1-v2/2810000/FCA4CA19-EECE-A34A-840D-E3A7E0051D79.root'
    ),
    secondaryFileNames = cms.untracked.vstring()
)

process.options = cms.untracked.PSet(
    IgnoreCompletely = cms.untracked.vstring(),
    Rethrow = cms.untracked.vstring(),
    TryToContinue = cms.untracked.vstring(),
    accelerators = cms.untracked.vstring('*'),
    allowUnscheduled = cms.obsolete.untracked.bool,
    canDeleteEarly = cms.untracked.vstring(),
    deleteNonConsumedUnscheduledModules = cms.untracked.bool(True),
    dumpOptions = cms.untracked.bool(True),
    emptyRunLumiMode = cms.obsolete.untracked.string,
    eventSetup = cms.untracked.PSet(
        forceNumberOfConcurrentIOVs = cms.untracked.PSet(
            allowAnyLabel_=cms.required.untracked.uint32
        ),
        numberOfConcurrentIOVs = cms.untracked.uint32(0)
    ),
    fileMode = cms.untracked.string('FULLMERGE'),
    forceEventSetupCacheClearOnNewRun = cms.untracked.bool(False),
    holdsReferencesToDeleteEarly = cms.untracked.VPSet(),
    makeTriggerResults = cms.obsolete.untracked.bool,
    modulesToCallForTryToContinue = cms.untracked.vstring(),
    modulesToIgnoreForDeleteEarly = cms.untracked.vstring(),
    numberOfConcurrentLuminosityBlocks = cms.untracked.uint32(0),
    numberOfConcurrentRuns = cms.untracked.uint32(1),
    numberOfStreams = cms.untracked.uint32(0),
    numberOfThreads = cms.untracked.uint32(2),
    printDependencies = cms.untracked.bool(False),
    sizeOfStackForThreadsInKB = cms.optional.untracked.uint32,
    throwIfIllegalParameter = cms.untracked.bool(True),
    wantSummary = cms.untracked.bool(False),
)

# Production Info
process.configurationMetadata = cms.untracked.PSet(
    annotation = cms.untracked.string('--step nevts:10'),
    name = cms.untracked.string('Applications'),
    version = cms.untracked.string('$Revision: 1.19 $')
)

# Output definition

process.NANOAODSIMoutput = cms.OutputModule("NanoAODOutputModule",
    compressionAlgorithm = cms.untracked.string('LZMA'),
    compressionLevel = cms.untracked.int32(9),
    dataset = cms.untracked.PSet(
        dataTier = cms.untracked.string('NANOAODSIM'),
        filterName = cms.untracked.string('')
    ),
    fileName = cms.untracked.string('file:step_nanoAODv15.root'),
    outputCommands = process.NANOAODSIMEventContent.outputCommands
)

# Additional output definition

# Other statements
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '150X_mc2018_realistic_v1', '')

# Path and EndPath definitions
process.nanoAOD_step = cms.Path(process.nanoSequenceMC)
process.endjob_step = cms.EndPath(process.endOfProcess)
process.NANOAODSIMoutput_step = cms.EndPath(process.NANOAODSIMoutput)

# Schedule definition
process.schedule = cms.Schedule(process.nanoAOD_step,process.endjob_step,process.NANOAODSIMoutput_step)
from PhysicsTools.PatAlgos.tools.helpers import associatePatAlgosToolsTask
associatePatAlgosToolsTask(process)

# customisation of the process.

# Automatic addition of the customisation function from Configuration.DataProcessing.Utils
from Configuration.DataProcessing.Utils import addMonitoring 

#call to customisation function addMonitoring imported from Configuration.DataProcessing.Utils
process = addMonitoring(process)

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.nano_cff
from PhysicsTools.NanoAOD.nano_cff import nanoAOD_customizeCommon 

#call to customisation function nanoAOD_customizeCommon imported from PhysicsTools.NanoAOD.nano_cff
process = nanoAOD_customizeCommon(process)

# Automatic addition of the customisation function from PhysicsTools.NanoAOD.custom_btv_cff
from PhysicsTools.NanoAOD.custom_btv_cff import BTVCustomNanoAOD 

#call to customisation function BTVCustomNanoAOD imported from PhysicsTools.NanoAOD.custom_btv_cff
process = BTVCustomNanoAOD(process)

# End of customisation functions


# Customisation from command line

process.source.delayReadingEventProducts = cms.untracked.bool(False)

# Add early deletion of temporary data products to reduce peak memory need
from Configuration.StandardSequences.earlyDeleteSettings_cff import customiseEarlyDelete
process = customiseEarlyDelete(process)
# End adding early deletion

# Drop unnecessary collections added by BTV customisation
process.NANOAODSIMoutput.outputCommands += [
    "drop nanoaodFlatTable_pfCandTable_*_*",
    "drop nanoaodFlatTable_jetPFCandTable_*_*",
    "drop nanoaodFlatTable_fatJetPFCandTable_*_*"
]
