import ROOT
ROOT.gROOT.SetBatch(True)
import sys, os
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import io_utils as io
import sf_cpp_functions as sf_cpp
import part_scores_functions as part_score
import selection
import samples as libsamples
import histos_baseline as libhistos
import plotting_utils as plotutil

RStyle = ROOT.gStyle
RStyle.SetPadLeftMargin(0.12)
RStyle.SetTitleOffset(0.9, "Y")
RStyle.SetPadRightMargin(0.25)
RStyle.SetPadGridX(1)
RStyle.SetPadGridY(1)

_weights = {
    'common': [ # use ttbar samples
        'norm_weight', 
        'L1PreFiringWeight_Nom', 
        'puWeight', 
        'tot_sf_weight', 
        'top_pt_weight',
        'btag_event_weight'
    ],
    'emu': [  
        'norm_weight', 
        'L1PreFiringWeight_Nom',
        'puWeight',
        'mu1_idsf',
        'mu1_isosf',
        #'mu_sf_weight',
        'e1_idsf',
        'e1_recosf',
        #'e_sf_weight',
        'trg_sf_weight',
        'top_pt_weight'
    ]
}

_unc_breakdown = {
    'emu': {
        'obj': { # systematics for trgger and object scale factors - included to the "tot_sf_weight" weight
            'base_exprUp'  : 'tot_weight/{sf_name}*{sf_name}Up', 
            'base_exprDown': 'tot_weight/{sf_name}*{sf_name}Down', 
            'branches' :[
                #'L1PreFiringWeight_Nom',
                'mu1_idsf', 
                'mu1_isosf', 
                'e1_idsf',
                'e1_recosf',
                'trg_sf_weight', 
                'top_pt_weight', 
                'puWeight',
            ],
        },
        'b-tag' : {
            'base_exprUp'  : 'tot_weight/btag_event_weight*{sf_name}Up',
            'base_exprDown': 'tot_weight/btag_event_weight*{sf_name}Down',
            'branches': [
                #'btag_event_weight_bc',     # only bc SFs
                'btag_event_weight_bccorr',
                'btag_event_weight_bcuncorr',
                #'btag_event_weight_light',  # only light-flavour SFs
                'btag_event_weight_lightcorr',
                'btag_event_weight_lightuncorr',
            ]
        },
        'JESR'  : {},
        'theory': {},
    }
}
_colors_long = [
    ROOT.TColor.GetColor("#3f90da"),		
    ROOT.TColor.GetColor("#ffa90e"),		
    ROOT.TColor.GetColor("#bd1f01"),		
    ROOT.TColor.GetColor("#94a4a2"),		
    ROOT.TColor.GetColor("#832db6"),		
    ROOT.TColor.GetColor("#a96b59"),		
    ROOT.TColor.GetColor("#e76300"),		
    ROOT.TColor.GetColor("#b9ac70"),		
    ROOT.TColor.GetColor("#717581"),		
    ROOT.TColor.GetColor("#92dadd"),
]
_colors_short = [
    ROOT.TColor.GetColor("#5790fc"),		
    ROOT.TColor.GetColor("#f89c20"),		
    ROOT.TColor.GetColor("#e42536"),		
    ROOT.TColor.GetColor("#964a8b"),		
    ROOT.TColor.GetColor("#9c9ca1"),		
    ROOT.TColor.GetColor("#7a21dd"),	
]
_sfs_name_color = {
# objects
    'L1PreFiringWeight_Nom': (
        'L1 prefire', ROOT.kBlue
    ),
    'puWeight': (
        'pileup', ROOT.TColor.GetColor("#3f90da")
    ),
    'tot_sf_weight': (
        'object SFs', ROOT.TColor.GetColor("#ffa90e")		
    ),
    'mu1_idsf': (
        '#mu ID', ROOT.TColor.GetColor("#bd1f01")
    ),
    'mu1_isosf': (
        '#mu iso', ROOT.TColor.GetColor("#94a4a2")
    ),
    'e1_idsf': (
        'e ID', ROOT.TColor.GetColor("#832db6")
    ),
    'e1_recosf': (
        'e reco', ROOT.TColor.GetColor("#a96b59")
    ),
    'top_pt_weight': (
        'top p_{T}', ROOT.TColor.GetColor("#e76300")
    ),
    'mu_sf_weight': (
        '#mu SFs (ID, iso)', ROOT.TColor.GetColor("#b9ac70")
    ),
    'e_sf_weight': (
        'e SFs (reco, ID)', ROOT.TColor.GetColor("#717581")
    ),
    'trg_sf_weight': (
        'trigger', ROOT.TColor.GetColor("#92dadd")
    ),
    # b-tag
    'btag_event_weight_bc': (
        'b-tag bc SFs', ROOT.TColor.GetColor("#964a8b")
    ),
    'btag_event_weight_bccorr': (
        '#splitline{b-tag bcSFs}{(corr)}', ROOT.TColor.GetColor("#964a8b")
    ),
    'btag_event_weight_bcuncorr': (
        '#splitline{b-tag bcSFs}{(uncorr)}', ROOT.TColor.GetColor("#964a8b")
    ),
    'btag_event_weight_light': (
        'b-tag lightSFs', ROOT.TColor.GetColor("#9c9ca1")
    ),
    'btag_event_weight_lightcorr': (
        '#splitline{b-tag lightSFs}{(corr)}', ROOT.TColor.GetColor("#9c9ca1")
    ),
    'btag_event_weight_lightuncorr': (
        '#splitline{b-tag lightSFs}{(uncorr)}', ROOT.TColor.GetColor("#9c9ca1")
    ),
}


def parse_arguments():
    parser = argparse.ArgumentParser(description="BsTauTau Plotter")
    parser.add_argument('--channels', nargs='+',  default=['emu'], help='Channels to process')
    parser.add_argument('--year', default='2018', choices=libsamples.years, type = str, help='Year of data taking')
    parser.add_argument('--unctype', default='obj',  help='Which group of systematic to test (obj, b-tag, JESR, theory)')  
    parser.add_argument('--outdir', default='plots/uncertainty', help="Output directory for plots and files")
    parser.add_argument('--test', action='store_true', default=False, help='Run a quick test with onbly signal sample')
    return parser.parse_args()

if __name__ == "__main__":

    args = parse_arguments()
    channels = args.channels
    channels = channels[0].split(',')
    year = args.year
    unctype = args.unctype
    outdir = args.outdir 
    
    used_mc_samples_names   = libsamples.mc_samples_names[:1]
    
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
        print(f"[+] created output directory {outdir}.") 

    samples = dict()
    tree_name = 'Events'

    for ch in channels:

        print(f"\n ----- CHANNEL: {ch} ----- ")
        # load input MC samples
        tree_dir                = '/eos/cms/store/group/phys_bphys/cbasile/BsTauTau-ttbar/test2018-v2/flat_ntuples/ntuples_%s_2018_ParT'%(ch)
        tree_dir_wsfs           = '%s/wsfs_snapshots/'%(tree_dir)
        tree_dir_btag_sfs       = '%s/btag_sfs_snapshots-sys/'%(tree_dir)
        tree_dir_filtered       = '%s/filtered_data_snapshots/'%(tree_dir)
        print(f" ... loading samples from {tree_dir}...")
        
        # load MC samples
        print(" ... loading MC samples")
        samples[ch] = dict()
        mc_samples = io.load_mc_samples(
            ch, used_mc_samples_names, year,
            libsamples.files_names, tree_name, 
            tree_dir, tree_dir_wsfs, tree_dir_btag_sfs, 
            libsamples.luminosity_2018, libsamples.cross_sections, 
            selection.trigger_selections, 
            use_ntuples_with_sfs = False, 
            compute_btag_sfs = False, 
            use_ntuples_with_btag_sfs= True, 
            part_samples = True
        )
        samples[ch].update(mc_samples)
        _norm_weights = _weights.get('common', [])
        _unc_set = _unc_breakdown.get(ch, {}).get(unctype, {})
        for k, sample in samples[ch].items():
            print(f"[{k}]")
            
            # compute total weight for each sample (nominal + variations)
            if not 'tot_weight' in sample.GetColumnNames():
                samples[ch][k]   = sf_cpp.combine_insert_weight(
                    samples[ch][k], 'tot_weight', 
                    _norm_weights, 
                    make_variations=True,
                )
        
            # vary each SF one at a time and compute the corresponding yields

            for sf_name in _unc_set.get('branches', []):
                print(f"\t- {sf_name}")

                varied_weightUp_list    = [w if w != sf_name else w.removesuffix('Nom') +'Up' for w in _norm_weights]
                varied_weightDown_list  = [w if w != sf_name else w.removesuffix('Nom') +'Down' for w in _norm_weights]
                
                varied_weightUp_expr    = _unc_set['base_exprUp'].format(sf_name = sf_name) #f'tot_weight/{sf_name}*{sf_name}Up'
                varied_weightDown_expr  = _unc_set['base_exprDown'].format(sf_name = sf_name) #f'tot_weight/{sf_name}*{sf_name}Down'
                print(f"\t UP [DOWN] variation:   {varied_weightUp_expr}  [{varied_weightDown_expr}]")
                samples[ch][k] = samples[ch][k].Define(f'tot_weight_{sf_name}Up',   varied_weightUp_expr)
                samples[ch][k] = samples[ch][k].Define(f'tot_weight_{sf_name}Down', varied_weightDown_expr)
                
    
        # -- PLOTTING --
        _histo_base = libhistos.histos_test 
        
        print(f"\n --- INITIALIZING HISTOGRAMS ---")
        # nominal yields 
        h_total_yield = plotutil.initialize_histograms(
            _histo_base, 
            samples,
            ch = ch,
            norm_weight = 'tot_weight',
            sys_uncertainty = False,
        )
        # up and down variations yields
        h_Up_yield, h_Down_yield = dict(), dict() 
        for sf_name in _unc_set.get('branches', []):
            h_Up_yield[sf_name] = plotutil.initialize_histograms(
                _histo_base, 
                samples,
                ch = ch,
                norm_weight = f'tot_weight_{sf_name}Up',
                sys_uncertainty = False,
            )
            h_Down_yield[sf_name] = plotutil.initialize_histograms(
                _histo_base, 
                samples,
                ch = ch,
                norm_weight = f'tot_weight_{sf_name}Down',
                sys_uncertainty = False,
            )
        
        # plotting
        print(f"\n --- PLOTTING ---")
        rootfile = ROOT.TFile(f'{outdir}/{ch}{year}-{unctype}_uncertainties.root', 'RECREATE')
        for var, v in h_total_yield.items(): # (var, {h_name: histo})
            print(f"\n> {var}")
            xlabel = _histo_base[ch].get(var, [])[1]
            for h_name, h in v.items():

                sample = h_name.removeprefix(f'{var}_')
                this_tag = f"{var}_{ch}-{unctype}_{sample}"
                
                # style nominal yield and plot
                plotutil.set_histogram_style(h, xlabel, 'Events', 0, libsamples.colours.get(sample, ROOT.kBlack))

                canv0 = ROOT.TCanvas(f'c_{this_tag}_nom',f'c_{this_tag}_nom', 1024, 800)
                canv0.cd()
                h.Draw('HIST E')
                canv0.SaveAs(f'plots/sf_uncertainties/{this_tag}_nominal.png')

                rootfile.cd()
                h.Write(f'{this_tag}')
                
                # uncertainties
                canv1 = ROOT.TCanvas(f'c_{this_tag}_unc',f'c_{this_tag}_unc', 1200, 800)
                up_stack = ROOT.THStack('up_stack', '')
                down_stack = ROOT.THStack('down_stack', '')
                legend = ROOT.TLegend(0.75, 0.2, 1.0, 0.9)
                legend.SetTextSize(0.045)
                legend.SetBorderSize(0)
                legend.SetFillStyle(0)
                legend.SetHeader("#splitline{solid:UP}{dashed:DOWN}", "L")

                # loop on SFs variations
        
                for isf, sf_name in enumerate(_unc_set.get('branches', [])):
                    print(f"\tSF: {sf_name}")
                    h_up    = (h_Up_yield[sf_name][var][h_name]).Clone()
                    h_up.SetDirectory(0)
                    h_down  = (h_Down_yield[sf_name][var][h_name]).Clone()
                    h_down.SetDirectory(0)
                    
                    
                    h_up.Divide(h.GetPtr())
                    h_down.Divide(h.GetPtr())
                    
                    # plot SF uncertainty
                    plotutil.set_histogram_style(
                        h_up,
                        xlabel, 'relative uncertainty',
                        0,
                        _colors_long[isf % len(_colors_long)], 
                    )
                    
                    plotutil.set_histogram_style(
                        h_down,
                        xlabel, 'relative uncertainty',
                        0,
                        _colors_long[isf % len(_colors_long)]
                    )
                    h_down.SetLineStyle(ROOT.kDashed)
                    
                    up_stack.Add(h_up)
                    down_stack.Add(h_down)
                    
                    legend.AddEntry(h_up, _sfs_name_color.get(sf_name, (sf_name, ROOT.kGray))[0], 'l')
                    
                    # save histograms in root file
                    rootfile.cd()
                    h_up.Write(f'{this_tag}_{sf_name}Up')
                    h_down.Write(f'{this_tag}_{sf_name}Down')

                # channel label
                channel_label = ROOT.TLatex()
                channel_label.SetNDC()
                channel_label.SetTextFont(42)
                channel_label.SetTextSize(0.05)
                
                # plot
                canv1.cd()
                up_stack.Draw('NOSTACK HIST')
                down_stack.Draw('NOSTACK HIST SAME')
                hist_list_up = up_stack.GetHists()
                one_h = hist_list_up.At(0)

                # total uncertainty 
                h_totunc_up   = one_h.Clone(f'{this_tag}_total_uncUp')
                h_totunc_up.SetDirectory(0)
                h_totunc_up.Reset()
                h_totunc_down = one_h.Clone(f'{this_tag}_total_uncDown')
                h_totunc_down.SetDirectory(0)
                h_totunc_down.Reset()

                for sf_h in hist_list_up:
                    for i in range(1, h_totunc_up.GetNbinsX()+1):
                        h_totunc_up.SetBinContent(i, h_totunc_up.GetBinContent(i) + (sf_h.GetBinContent(i) - 1)**2 if sf_h.GetBinContent(i) > 0 else 0)
                for i in range(1, h_totunc_up.GetNbinsX()+1):
                    h_totunc_up.SetBinContent(i, 1 + h_totunc_up.GetBinContent(i)**0.5)
                plotutil.set_histogram_style(
                    h_totunc_up,
                    xlabel, 'total relative uncertainty',
                    0,
                    ROOT.kBlack, 
                )
                legend.AddEntry(h_totunc_up, 'total', 'l')
                for sf_h in down_stack.GetHists():
                    for i in range(1, h_totunc_down.GetNbinsX()+1):
                        h_totunc_down.SetBinContent(i, h_totunc_down.GetBinContent(i) + (sf_h.GetBinContent(i) - 1)**2 if sf_h.GetBinContent(i) > 0 else 0)
                for i in range(1, h_totunc_down.GetNbinsX()+1):
                    h_totunc_down.SetBinContent(i, 1 - h_totunc_down.GetBinContent(i)**0.5)
                plotutil.set_histogram_style(
                    h_totunc_down,
                    xlabel, 'total relative uncertainty',
                    0,
                    ROOT.kBlack, 
                )
                h_totunc_down.SetLineStyle(ROOT.kDashed)
                
                # adjuts axes and save
                up_stack.GetXaxis().SetTitle(one_h.GetXaxis().GetTitle())
                up_stack.GetYaxis().SetTitle('Relative Uncertainty')

                h_totunc_up.Draw('HIST SAME')
                h_totunc_down.Draw('HIST SAME')

                dy = h_totunc_up.GetMaximum() - 1. + 0.05
                up_stack.SetMaximum(1. + dy)
                up_stack.SetMinimum(1. - dy)
                
                line = ROOT.TLine(one_h.GetXaxis().GetXmin(), 1.0, one_h.GetXaxis().GetXmax(), 1.0) 
                line.SetLineColor(ROOT.kGray+2)
                line.SetLineStyle(ROOT.kDashed)
                canv1.Modified()
                legend.Draw()
                channel_label.DrawLatex(0.2, 0.85, f"{libsamples.ch_labels.get(ch, ch)} - {sample}")
                line.Draw("SAME")
                
                canv1.SaveAs(f'{outdir}/{this_tag}_uncertainty.png')
                #canv1.SetLogy()
                #canv1.SaveAs(f'plots/sf_uncertainties/{this_tag}_uncertainty-log.png')
    
    rootfile.Close()
                    
                    
                
                

            



 
