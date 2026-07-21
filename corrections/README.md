# Preselection and MC correction for $Bs\to\tau\tau$

## Onetime setup
```
cmsrel CMSSW_13_0_10
cd CMSSW_13_0_10/src/
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools 
cd PhysicsTools/NanoAODTools
cmsenv
scram b
cd ../../../../ 
git clone --recursive git@github.com:friti/BsTauTau.git --branch bstautau-dev
cd BsTauTau/corrections/
```

## At login
```
cd CMSSW_13_0_10/src/PhysicsTools/NanoAODTools
cmsenv
cd ../../../../BsTauTau/corrections/
```

## Main usage: apply preselection and SF corrections

```bash
python main.py --input inputs/datamc_2018_test-v2.yml [--outdirectory <path>] [--channels <ch1> <ch2> ...] [--test]
```

| Option | Short | Default | Description |
|---|---|---|---|
| `--input` | `-i` | required | `.yml` file with input ntuple locations and metadata |
| `--outdirectory` | `-o` | from `.yml` | Output directory for corrected ntuples (overrides `.yml` value) |
| `--channels` | | `emu` | One or more decay channels to process |
| `--test` | `-t` | off | Test mode: runs on a single MC sample |

Supported channels: `mu`, `e`, `emu`, `mumu`, `ee`.

### Input configuration file

The input `.yml` file specifies paths and common metadata:

```yaml
MC:
  inpath_template: "/eos/cms/.../ntuples_{channel}_2018_ParT"
  outpath_template: "/eos/cms/.../ntuples_{channel}_2018_ParT/sfs_applied"
data:
  inpath_template: "/eos/cms/.../ntuples_{channel}_2018_ParT"
  outpath_template: "/eos/cms/.../ntuples_{channel}_2018_ParT/sfs_applied"
common:
  year: 2018
  treename: Events
```

`{channel}` is substituted at runtime with the channel being processed.
See `inputs/datamc_TEMPLATE.yml` for a blank template and `inputs/datamc_2018_test-v2.yml` for a concrete example.

## Processing pipeline

For each channel and MC sample, `main.py` runs the following steps in order:

1. **Trigger selection** — applies the OR of per-dataset HLT paths defined in `data_toolkit/selection.py`
2. **Variable definition** — computes derived quantities (invariant mass, transverse mass, jet masks, b-tagging conditions)
3. **Preselection** — filters on lepton pT/η, MET, and b-tagging/jet requirements (channel-dependent)
4. **Jet selection** — requires at least one jet passing minimum kinematics (pT > 20 GeV, |η| < 2.5, jetId ≥ 2)
5. **Snapshot** — saves the skimmed tree to a temporary ROOT file in `tmp_output/`
6. **Scale factor computation** (chunked, via `sf_toolkit`):
   - Muon ID and isolation SFs (nominal + up/down)
   - Electron ID, reco, and trigger SFs (nominal + up/down)
   - Trigger SFs (channel-dependent)
   - Top pT reweighting (applied to `tt` and `bstautau` samples)
   - b-tag SFs (channel-specific working point)
7. **Consistency check** — verifies no events are lost or duplicated between the preselected and SF files
8. **Merge** — adds the SF branches back to the skimmed tree via `TTree::AddFriend` and writes the final output ntuple

Output files are named `<sample>_wsfs.root` and written to the `outpath_template` directory from the `.yml`.

## MC samples

| Key | ROOT file | Process |
|---|---|---|
| `tt_fullylep` | `TTTo2L2Nu` | $t\bar{t}$ fully leptonic |
| `tt_semilep` | `TTToSemileptonic` | $t\bar{t}$ semi-leptonic |
| `tt_had` | `TTToHadronic` | $t\bar{t}$ hadronic |
| `ww` / `wz` / `zz` | `WW` / `WZ` / `ZZ` | Diboson |
| `st_s`, `st_antit`, `st_tw`, `st_antitw` | `ST_*` | Single top |
| `w` / `wext` | `W` / `W_ext` | W+jets |
| `dy` | `DY` | Drell-Yan |
| `bstautau` | `ttbarToBsToTauTau` | Signal: $t\bar{t} \to B_s \to \tau\tau$ |

## Additional scripts

- **`genmatching.py`** — studies the efficiency of matching $B_s$ to b-tagged jets at generator level (CHS and PUPPI jets). Run with `--input` pointing to a signal ntuple.
