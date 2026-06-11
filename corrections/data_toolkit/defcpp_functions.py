import ROOT

##### invariant mass function
ROOT.gInterpreter.Declare("""
double compute_inv_mass(double pt1, double eta1, double phi1, double mass1, double pt2, double eta2, double phi2, double mass2) {
  TLorentzVector v1, v2;
  v1.SetPtEtaPhiM(pt1, eta1, phi1, mass1);
  v2.SetPtEtaPhiM(pt2, eta2, phi2, mass2);
  return (v1 + v2).M();
}
""")

## define MT (transverse mass)
ROOT.gInterpreter.Declare("""
double compute_mt(double pt, double phi, double met, double met_phi) {
  return sqrt(2 * pt * met * (1 - cos(phi - met_phi)));
}
""")


ROOT.gInterpreter.Declare("""
ROOT::RVec<int> findIndicesOfBsTauTau(const ROOT::RVec<int>& isBsTauTau) {
    ROOT::RVec<int> indices;
    for (size_t i = 0; i < isBsTauTau.size(); ++i) {
        if (isBsTauTau[i] == 1){
//std::cout<<"index new method "<<i<<std::endl;
            indices.push_back(i);}
    }
    return indices;
}
""")

ROOT.gInterpreter.Declare(R"""
// ---------- small utilities ----------
float dR(float e1,float p1,float e2,float p2){
  float dEta = e1-e2;
  float dPhi = std::fabs(p1-p2);
  if(dPhi>M_PI) dPhi = 2*M_PI-dPhi;
  return std::sqrt(dEta*dEta+dPhi*dPhi);
}
bool isBs(int pdg){ return std::abs(pdg)==531; }
bool isTau(int pdg){ return std::abs(pdg)==15; }


ROOT::RVec<int> findSignalBs(const ROOT::RVec<int>& pdg) {
    ROOT::RVec<int> out;
    for(size_t i = 0; i < pdg.size(); ++i) {
        if (isBs(pdg[i])) {  // Check if it's a B_s meson
//std::cout<<"index old method "<<i<<std::endl;
//std::cout"I have a Bs "<<pdg[i]<<" index "<<i<<std::endl;
            out.push_back(i);  // Add the index of the B_s meson to the output
        }
    }
    return out;
}
// ---------- match those B_s to jets ----------
ROOT::RVec<int> matchSignalBsToJets(const ROOT::RVec<int>& bsIdx,
                                    const ROOT::RVec<float>& gp_eta,
                                    const ROOT::RVec<float>& gp_phi,
                                    const ROOT::RVec<float>& jet_pt,
                                    const ROOT::RVec<float>& jet_eta,
                                    const ROOT::RVec<float>& jet_phi,
                                    const ROOT::RVec<float>& jet_btag,
                                    float btagWP){
  ROOT::RVec<int> matched;
  for(int b : bsIdx){
    float bestDR = 0.4;
    int   bestJ  = -1;
    for(size_t j=0;j<jet_pt.size();++j){
      if(jet_pt[j]<20 || std::fabs(jet_eta[j])>2.5) continue;
      if(jet_btag[j] < btagWP)                       continue;
      float dr = dR(gp_eta[b],gp_phi[b],jet_eta[j],jet_phi[j]);
      if(dr<bestDR){ bestDR = dr; bestJ = j; }
    }
    if(bestJ>=0) matched.push_back(bestJ);
  }
  return matched;
}

// ---------- build a per-jet boolean mask ----------
ROOT::RVec<int> maskFromIndices(const ROOT::RVec<int>& idx, std::size_t nJets){
  ROOT::RVec<int> m(nJets, 0);
  for (int i : idx) {
    if (i >= 0 && (std::size_t)i < nJets)
      m[i] = 1;
  }
  return m;
}
""")