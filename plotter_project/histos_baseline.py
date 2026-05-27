# histos definition
# histos definition
# histos definition
import ROOT

histos = dict()
histos_test = dict() # only few to test

histos_flavor = dict()

## common branches
histos_jets = dict()
histos_general = dict()

histos_jets_part = dict()

histos_interesting_jets = dict() ## needed for flavor based histograms
histos_interesting_jets_part = dict() ## needed for flavor based histograms

'''
histos_jets['nj'] = (ROOT.RDF.TH1DModel('nj'     , '',20,     0,     20), 'N jets'         , 1)
histos_jets['j_pt'] = (ROOT.RDF.TH1DModel('j_pt', '', 50, 0, 200), 'Jet pT', 1)
histos_jets['j_eta'] = (ROOT.RDF.TH1DModel('j_eta', '', 50, -2.5, 2.5), 'Jet eta', 1)
histos_jets['j_phi'] = (ROOT.RDF.TH1DModel('j_phi', '', 50, -3.14, 3.14), 'Jet phi', 1)
histos_general['j_m'] = (ROOT.RDF.TH1DModel('j_m', '', 50, 0, 200), 'Jet mass', 1)
histos_general['j_puid'] = (ROOT.RDF.TH1DModel('j_puid', '', 5, 0, 5), 'Jet PUID', 1)
histos_general['j_jetid'] = (ROOT.RDF.TH1DModel('j_jetid', '', 5, 0, 5), 'Jet ID', 1)
histos_general['j_deepflavB'] = (ROOT.RDF.TH1DModel('j_deepflavB', '', 50, 0, 1), 'Jet DeepFlavB', 1)
histos_general['j_hadronFlavour'] = (ROOT.RDF.TH1DModel('j_hadronFlavour', '', 10, -5, 5), 'Jet Hadron Flavour', 1)
'''

# histo with minimum jet selection
histos_general['selected_jets_for_histo_njets'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_njets', '', 10, 0, 10), 'N jets (pT > min_jet_pt)', 1)
histos_jets['selected_jets_for_histo_pt'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_pt', '', 50, 0, 200), 'Jet pT (pT > min_jet_pt)', 1)
histos_jets['selected_jets_for_histo_eta'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_eta', '', 50, -2.5, 2.5), 'Jet eta (pT > min_jet_pt)', 1)
histos_jets['selected_jets_for_histo_phi'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_phi', '', 50, -3.14, 3.14), 'Jet phi (pT > min_jet_pt)', 1)
histos_jets['selected_jets_for_histo_m'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_ma', '', 50, 0, 50), 'Jet mass (pT > min_jet_pt)', 1)
histos_jets['selected_jets_for_histo_puid'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_puid', '', 5, 0, 5), 'Jet PUID (pT > min_jet_pt)', 1)
histos_jets['selected_jets_for_histo_jetid'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_jetid', '', 7, 0, 7), 'Jet ID (pT > min_jet_pt)', 1)
histos_jets['selected_jets_for_histo_deepflavB'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_deepflavB', '', 50, 0, 1), 'Jet DeepFlavB (pT > min_jet_pt)', 1)
#histos_jets['selected_jets_for_histo_ht'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_ht', '', 30, 20, 500), 'HT', 1)
histos_jets_part['selected_jets_for_histo_ParTRawB'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_ParTRawB', '', 30, 0, 0.4), 'ParTRawB', 1)
histos_jets_part['selected_jets_for_histo_ParTRawC'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_ParTRawC', '', 30, 0, 0.5), 'ParTRawC', 1)
histos_jets_part['selected_jets_for_histo_ParTRawOther'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_ParTRawOther', '', 30, 0, 1), 'ParTRawOther', 1)
histos_jets_part['selected_jets_for_histo_ParTRawSingletau'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_ParTRawSingletau', '', 30, 0, 0.6), 'ParTRawSingletau', 1)
histos_jets_part['selected_jets_for_histo_ParTRawTauhtaue'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_ParTRawTauhtaue', '', 30, 0, 0.4), 'ParTRawTauhtaue', 1)
histos_jets_part['selected_jets_for_histo_ParTRawTauhtauh'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_ParTRawTauhtauh', '', 30, 0, 0.4), 'ParTRawTauhtauh', 1)
histos_jets_part['selected_jets_for_histo_ParTRawTauhtaumu'] = (ROOT.RDF.TH1DModel('selected_jets_for_histo_ParTRawTauhtaumu', '', 30, 0, 0.2), 'ParTRawTauhtaumu', 1)

# histo with btagged jet selection

histos_general['btagged_loose_jets_pt_above_20_for_histo_njets'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_njets', '', 10, 0, 10), 'N jets (pT > min_jet_pt)', 1)
histos_interesting_jets['btagged_loose_jets_pt_above_20_for_histo_pt'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_pt', '', 50, 0, 200), 'Jet pT (pT > min_jet_pt)', 1)
histos_interesting_jets['btagged_loose_jets_pt_above_20_for_histo_eta'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_eta', '', 50, -2.5, 2.5), 'Jet eta (pT > min_jet_pt)', 1)
histos_interesting_jets['btagged_loose_jets_pt_above_20_for_histo_phi'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_phi', '', 50, -3.14, 3.14), 'Jet phi (pT > min_jet_pt)', 1)
histos_interesting_jets['btagged_loose_jets_pt_above_20_for_histo_m'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_m', '', 50, 0, 50), 'Jet mass (pT > min_jet_pt)', 1)
histos_interesting_jets['btagged_loose_jets_pt_above_20_for_histo_puid'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_puid', '', 5, 0, 5), 'Jet PUID (pT > min_jet_pt)', 1)
#histos_jets['btagged_loose_jets_pt_above_20_for_histo_ht'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_ht', '', 30, 20, 500), 'HT', 1)
histos_interesting_jets_part['btagged_loose_jets_pt_above_20_for_histo_ParTRawB'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_ParTRawB', '', 30, 0, 0.4), 'ParTRawB', 1)
histos_interesting_jets_part['btagged_loose_jets_pt_above_20_for_histo_ParTRawC'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_ParTRawC', '', 30, 0, 0.5), 'ParTRawC', 1)
histos_interesting_jets_part['btagged_loose_jets_pt_above_20_for_histo_ParTRawOther'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_ParTRawOther', '', 30, 0, 1), 'ParTRawOther', 1)
histos_interesting_jets_part['btagged_loose_jets_pt_above_20_for_histo_ParTRawSingletau'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_ParTRawSingletau', '', 30, 0, 0.6), 'ParTRawSingletau', 1)
histos_interesting_jets_part['btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtaue'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtaue', '', 30, 0, 0.4), 'ParTRawTauhtaue', 1)
histos_interesting_jets_part['btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtauh'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtauh', '', 30, 0, 0.4), 'ParTRawTauhtauh', 1)
histos_interesting_jets_part['btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtaumu'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtaumu', '', 30, 0, 0.2), 'ParTRawTauhtaumu', 1)

histos_general['btagged_loose_jets_pt_above_30_for_histo_njets'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_njets', '', 10, 0, 10), 'N jets (pT > min_jet_pt)', 1)
histos_jets['btagged_loose_jets_pt_above_30_for_histo_pt'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_pt', '', 50, 0, 200), 'Jet pT (pT > min_jet_pt)', 1)
histos_jets['btagged_loose_jets_pt_above_30_for_histo_eta'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_eta', '', 50, -2.5, 2.5), 'Jet eta (pT > min_jet_pt)', 1)
histos_jets['btagged_loose_jets_pt_above_30_for_histo_phi'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_phi', '', 50, -3.14, 3.14), 'Jet phi (pT > min_jet_pt)', 1)
histos_jets['btagged_loose_jets_pt_above_30_for_histo_m'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_m', '', 50, 0, 50), 'Jet mass (pT > min_jet_pt)', 1)
histos_jets['btagged_loose_jets_pt_above_30_for_histo_puid'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_puid', '', 5, 0, 5), 'Jet PUID (pT > min_jet_pt)', 1)
histos_jets['btagged_loose_jets_pt_above_30_for_histo_jetid'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_jetid', '', 7, 0, 7), 'Jet ID (pT > min_jet_pt)', 1)
histos_jets['btagged_loose_jets_pt_above_30_for_histo_deepflavB'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_deepflavB', '', 50, 0, 1), 'Jet DeepFlavB (pT > min_jet_pt)', 1)
#histos_jets['btagged_loose_jets_pt_above_30_for_histo_ht'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_ht', '', 30, 20, 500), 'HT', 1)
histos_jets_part['btagged_loose_jets_pt_above_30_for_histo_ParTRawB'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_ParTRawB', '', 30, 0, 0.4), 'ParTRawB', 1)
histos_jets_part['btagged_loose_jets_pt_above_30_for_histo_ParTRawC'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_ParTRawC', '', 30, 0, 0.5), 'ParTRawC', 1)
histos_jets_part['btagged_loose_jets_pt_above_30_for_histo_ParTRawOther'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_ParTRawOther', '', 30, 0, 1), 'ParTRawOther', 1)
histos_jets_part['btagged_loose_jets_pt_above_30_for_histo_ParTRawSingletau'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_ParTRawSingletau', '', 30, 0, 0.6), 'ParTRawSingletau', 1)
histos_jets_part['btagged_loose_jets_pt_above_30_for_histo_ParTRawTauhtaue'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_ParTRawTauhtaue', '', 30, 0, 0.4), 'ParTRawTauhtaue', 1)
histos_jets_part['btagged_loose_jets_pt_above_30_for_histo_ParTRawTauhtauh'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_ParTRawTauhtauh', '', 30, 0, 0.4), 'ParTRawTauhtauh', 1)
histos_jets_part['btagged_loose_jets_pt_above_30_for_histo_ParTRawTauhtaumu'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_30_for_histo_ParTRawTauhtaumu', '', 30, 0, 0.2), 'ParTRawTauhtaumu', 1)



histos_general['PuppiMET_phi'] = (ROOT.RDF.TH1DModel('PuppiMET_phi', '', 20, -3.14, 3.14), 'MET phi', 1)
histos_general['PuppiMET_pt'] = (ROOT.RDF.TH1DModel('PuppiMET_pt', '', 30, 0, 200), 'MET pt', 1)


histos['mu'] = dict()
histos['e'] = dict()
histos['emu'] = dict()
histos_test['emu'] = dict()
histos['mumu'] = dict()
histos['ee'] = dict()

##common branches for electrons
histos_general_e = dict()
histos_general_e['e1_pt'] = (ROOT.RDF.TH1DModel('e1_pt', '', 20, 0, 200), 'Electron 1 pt', 1)
histos_general_e['e1_eta'] = (ROOT.RDF.TH1DModel('e1_eta', '', 20, -2.5, 2.5), 'Electron 1 eta', 1)
histos_general_e['e1_phi'] = (ROOT.RDF.TH1DModel('e1_phi', '', 20, -3.14, 3.14), 'Electron 1 phi', 1)
histos_general_e['e1_dxy'] = (ROOT.RDF.TH1DModel('e1_dxy', '', 20, -0.02, 0.02), 'Electron 1 dxy', 1)
histos_general_e['e1_dz'] = (ROOT.RDF.TH1DModel('e1_dz', '', 20, -0.1, 0.1), 'Electron 1 dz', 1)
histos_general_e['e1_charge'] = (ROOT.RDF.TH1DModel('e1_charge', '',3, -1.5, 1.5), 'Electron 1 charge', 1)
histos_general_e['MT_e1_MET'] = (ROOT.RDF.TH1DModel('MT_e1_MET', '',50, -10, 150), 'MT', 1)

## common branches for muons
histos_general_mu = dict()
histos_general_mu['mu1_pt'] = (ROOT.RDF.TH1DModel('mu1_pt', '', 50, 0, 200), 'Muon 1 pT', 1)
histos_general_mu['mu1_eta'] = (ROOT.RDF.TH1DModel('mu1_eta', '', 50, -2.5, 2.5), 'Muon 1 eta', 1)
histos_general_mu['mu1_phi'] = (ROOT.RDF.TH1DModel('mu1_phi', '', 50, -3.14, 3.14), 'Muon 1 phi', 1)
histos_general_mu['mu1_dxy'] = (ROOT.RDF.TH1DModel('mu1_dxy', '', 50, -0.5, 0.5), 'Muon 1 dxy', 1)
histos_general_mu['mu1_dz'] = (ROOT.RDF.TH1DModel('mu1_dz', '', 50, -0.5, 0.5), 'Muon 1 dz', 1)
histos_general_mu['mu1_charge'] = (ROOT.RDF.TH1DModel('mu1_charge', '', 3, -1.5, 1.5), 'Muon 1 charge', 1)
histos_general_mu['MT_mu1_MET'] = (ROOT.RDF.TH1DModel('MT_mu1_MET', '',50, -10, 150), 'MT', 1)

histos['mu'].update(histos_jets)
histos['e'].update(histos_jets)
histos['emu'].update(histos_jets)
histos['mumu'].update(histos_jets)
histos['ee'].update(histos_jets)                                                 

histos['mu'].update(histos_general)
histos['e'].update(histos_general)
histos['emu'].update(histos_general)
histos['mumu'].update(histos_general)
histos['ee'].update(histos_general)


histos['mu'].update(histos_interesting_jets)
histos['e'].update(histos_interesting_jets)
histos['emu'].update(histos_interesting_jets)
histos['mumu'].update(histos_interesting_jets)
histos['ee'].update(histos_interesting_jets)

histos['mu'].update(histos_general_mu)
histos['e'].update(histos_general_e)
histos['emu'].update(histos_general_e)
histos['emu'].update(histos_general_mu)
histos['mumu'].update(histos_general_mu)
histos['ee'].update(histos_general_e)

## add second lepton

histos['ee']['e2_pt'] = (ROOT.RDF.TH1DModel('e2_pt', '', 20, 0, 500), 'Electron 2 pt', 1)
histos['ee']['e2_eta'] = (ROOT.RDF.TH1DModel('e2_eta', '', 20, -2.5, 2.5), 'Electron 2 eta', 1)
histos['ee']['e2_phi'] = (ROOT.RDF.TH1DModel('e2_phi', '', 20, -3.14, 3.14), 'Electron 2 phi', 1)
histos['ee']['e2_dxy'] = (ROOT.RDF.TH1DModel('e2_dxy', '', 20, 0, 1), 'Electron 2 dxy', 1)
histos['ee']['e2_dz'] = (ROOT.RDF.TH1DModel('e2_dz', '', 20, 0, 1), 'Electron 2 dz', 1)
histos['ee']['e2_charge'] = (ROOT.RDF.TH1DModel('e2_charge', '',3, -1.5, 1.5), 'Electron 2 charge', 1)
histos['ee']['MT_e2_MET'] = (ROOT.RDF.TH1DModel('MT_e2_MET', '',50, -10, 150), 'MT', 1)

histos['mumu']['mu2_pt'] = (ROOT.RDF.TH1DModel('mu2_pt', '', 50, 0, 200), 'Muon 2 pT', 1)
histos['mumu']['mu2_eta'] = (ROOT.RDF.TH1DModel('mu2_eta', '', 50, -2.5, 2.5), 'Muon 2 eta', 1)
histos['mumu']['mu2_phi'] = (ROOT.RDF.TH1DModel('mu2_phi', '', 50, -3.14, 3.14), 'Muon 2 phi', 1)
histos['mumu']['mu2_dxy'] = (ROOT.RDF.TH1DModel('mu2_dxy', '', 50, -0.5, 0.5), 'Muon 2 dxy', 1)
histos['mumu']['mu2_dz'] = (ROOT.RDF.TH1DModel('mu2_dz', '', 50, -0.5, 0.5), 'Muon 2 dz', 1)
histos['mumu']['mu2_charge'] = (ROOT.RDF.TH1DModel('mu2_charge', '', 3, -1.5, 1.5), 'Muon 2 charge', 1)
histos['mumu']['inv_mass'] = (ROOT.RDF.TH1DModel('inv_mass', '', 40, 40, 200), 'inv mass', 1)
histos['mumu']['MT_mu2_MET'] = (ROOT.RDF.TH1DModel('MT_mu2_MET', '',50, -10, 150), 'MT', 1)
#histos['mumu']['inv_mass'] = (ROOT.RDF.TH1DModel('inv_mass', '', 40, 0, 80), 'inv mass', 1)

histos['emu']['inv_mass'] = (ROOT.RDF.TH1DModel('inv_mass', '', 50, 10, 200), 'inv mass', 1)
histos['ee']['inv_mass'] = (ROOT.RDF.TH1DModel('inv_mass', '', 50, 10, 200), 'inv mass', 1)


## Only histos for flavor plotting, I am interested only in jet-based plots (not events based)
histos_flavor['emu'] = dict()
histos_flavor['mumu'] = dict()
histos_flavor['ee'] = dict()
histos_flavor['e'] = dict()
histos_flavor['mu'] = dict()



histos_flavor['emu'].update(histos_interesting_jets)
histos_flavor['mumu'].update(histos_interesting_jets)
histos_flavor['ee'].update(histos_interesting_jets)
histos_flavor['e'].update(histos_interesting_jets)
histos_flavor['mu'].update(histos_interesting_jets)

histos_test['emu']['e1_pt']  = (ROOT.RDF.TH1DModel('e1_pt', '', 20, 0, 200), 'electron p_{T} (GeV)', 1)
#histos_test['emu']['mu1_pt'] = (ROOT.RDF.TH1DModel('mu1_pt', '', 20, 0, 200), 'muon p_{T} (GeV)', 1)
#histos_test['emu']['inv_mass'] = (ROOT.RDF.TH1DModel('inv_mass', '', 50, 10, 200), 'inv mass', 1)
histos_test['emu']['btagged_loose_jets_pt_above_20_for_histo_part_all_sig_frac'] = (ROOT.RDF.TH1DModel('btagged_loose_jets_pt_above_20_for_histo_part_all_sig_frac', '', 20, 0, 1), 'sig frac', 1)