# Run NanoAODs adding our parT branch

## Setup environment
`ssh lxplus8` or access the singularity with `cmssw-el8`
```
git clone --recursive git@github.com:elenavernazza/BsTauTau.git
cd BsTauTau/make_samples/nano_with_part_branch

export SCRAM_ARCH=el8_amd64_gcc12
cmsrel CMSSW_15_0_18
cd CMSSW_15_0_18/src/
cmsenv
git cms-init

git cms-addpkg PhysicsTools/NanoAOD
git cms-addpkg PhysicsTools/PatAlgos
git cms-addpkg RecoBTag

## changes with new parT branches
git cms-merge-topic -u elenavernazza:MyParT_CMSSW_15_0_18

scram b -j8

cd ../..
```

Now we need to copy the model in the right directory
```
mkdir -p CMSSW_15_0_18/src/RecoBTag/Combined/data/UParTAK4/PUPPI/BsTauTau
cp part_run3_bstautau_btag_edge_sumref.onnx CMSSW_15_0_18/src/RecoBTag/Combined/data/UParTAK4/PUPPI/BsTauTau/part_run3_bstautau_btag_edge_sumref.onnx
```
To test it locally
```
cmsDriver.py --step NANO:@BTV \
 --eventcontent NANOAODSIM --datatier NANOAODSIM \
 --customise Configuration/DataProcessing/Utils.addMonitoring \
 --conditions 150X_mc2018_realistic_v1 --era Run2_2018,run2_nanoAOD_106Xv2 \
 --python_filename B2G-RunIISummer20UL18NanoAODv9-07124_1_cfg.py \
 --fileout file:TOP-RunIISummer20UL18NanoAODv15-00048_NANOAODSIM.root \
 --filein "dbs:/ttbarToBsToTauTau_BsFilter_TauTauFilter_TuneCP5_13TeV-pythia8-evtgen/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2/MINIAODSIM" \
 -n 10 --mc 
```

# WIP: condor submission

## Send jobs on CRAB (RECOMMENDED)
Use the `multisubmitter_crab_data.py` and `multisubmitter_crab_mc.py` `submit_on_crab_template.py`.
Since these are many and big jobs, crab is better.

## Send jobs on CONDOR
Use the `MultiSubmit.py` and `production_2024.sh`.
