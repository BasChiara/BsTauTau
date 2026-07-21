"""
    
"""

import ROOT
ROOT.gROOT.SetBatch(True)
RStyle = ROOT.gStyle
RStyle.SetPadLeftMargin(0.12)
RStyle.SetTitleOffset(0.9, "Y")
RStyle.SetPadRightMargin(0.25)
RStyle.SetPadGridX(1)
RStyle.SetPadGridY(1)

import sys, os
import yaml
import argparse
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
import io_utils as io
import selection
import histos_baseline as libhistos
import samples as libsamples
import plotting_utils as pu


def parse_arguments():
    parser = argparse.ArgumentParser(description="Tagger signal separation power")
    parser.add_argument('-i', '--input', 
                        required=True, 
                        help='input .root file with histograms'
                        )
    parser.add_argument('--channels', 
                        nargs='+',  default=['emu'], 
                        help='Channels to process'
                        )
    parser.add_argument('--year', 
                        default='2018', choices=libsamples.years, type = str, 
                        help='Year of data taking'
                        )
    parser.add_argument('--outdir',
                        default='plots/uncertainty', 
                        help="Output directory for plots and files"
                        )
    parser.add_argument('--test', 
                        action='store_true', 
                        default=False, 
                        help='Run a quick test with only signal sample'
                        )
    return parser.parse_args()

channel_label = {
    'emu': 'e#mu',
    'mumu': '#mu#mu',
    'ee': 'ee',
    'e' : 'e',
    'mu': '#mu',
}
signal_scale = 50

if __name__ == "__main__":
    args        = parse_arguments()
    with open(args.input, 'r') as f: # parse input file
        input_cfg = yaml.safe_load(f)
    inMC_cfg      = input_cfg.get('MC', {})
    channels    = args.channels
    year        = input_cfg.get('year', args.year)
    outdir      = args.outdir
    test        = args.test
    
    # MC samples
    used_mc_samples_names   = ['tt_fullylep', 'bstautau'] if test else libsamples.mc_samples_names
    tree_name               = inMC_cfg.get('tree_name', 'Events')
    print(f" ... processing MC samples: {used_mc_samples_names}")
    print(f" ... processing channels: {channels}")

    # Create output directory if it doesn't exist
    os.makedirs(outdir, exist_ok=True)
    
    samples = dict()
    # labels for channels
    ch_label = ROOT.TLatex()
    ch_label.SetNDC()
    ch_label.SetTextFont(42)
    ch_label.SetTextSize(0.06)

    channel_colors = {
        'emu'  : ROOT.kGreen + 2,
        'mumu' : ROOT.kBlue + 1,
        'ee'   : ROOT.kRed + 1,
        'e'    : ROOT.kOrange + 1,
        'mu'   : ROOT.kViolet + 1,
    }
    roc_graphs = {}  # hdir_name -> {channel: TGraph}

    for channel in channels:
        print(f"\n ---- CHANNEL {channel} ----")
        
        #tree_dir            = inMC_cfg.get('inpath_template', {}).format(channel=channel)
        #tree_dir_wsfs       = inMC_cfg.get('inpath_template_wsfs', {}).format(channel=channel)
        #tree_dir_btag_sfs   = inMC_cfg.get('inpath_template_btag_sfs', {}).format(channel=channel)
        
        #samples[channel] = dict()
        #mc_samples = io.load_mc_samples(
        #    channel, used_mc_samples_names, year,
        #    libsamples.files_names, tree_name, 
        #    tree_dir, tree_dir_wsfs, tree_dir_btag_sfs, 
        #    libsamples.luminosity_2018, libsamples.cross_sections, 
        #    selection.trigger_selections, 
        #    use_ntuples_with_sfs = False, 
        #    compute_btag_sfs = False, 
        #    use_ntuples_with_btag_sfs= True, 
        #    part_samples = True
        #)
        #samples[channel].update(mc_samples)

        # -- PLOTTING --
        # get the histo file
        _this_hpath = inMC_cfg.get('plotter_histos', None)
        if not _this_hpath or not os.path.isfile(_this_hpath):
            raise RuntimeError(f"Input histograms file {_this_hpath} does not exist")
        _this_hfile = ROOT.TFile.Open(_this_hpath, 'READ')
        
        # loop on directories in the channel folder
        for h_key in _this_hfile.Get(channel).GetListOfKeys():
            hdir_name = h_key.GetName()
            if not h_key.IsFolder(): continue
            print(f"  > histo {hdir_name}")
            thisoutpath = os.path.join(outdir, channel, hdir_name+".{ext}")
            os.makedirs(os.path.dirname(thisoutpath), exist_ok=True)
            
            # navigate into [histo_name]/bstautau_not_scaled/lin
            hdir = _this_hfile.Get(f"{channel}/{hdir_name}/bstautau_not_scaled/lin")
            if not hdir:
                print(f"    WARNING: bstautau_not_scaled not found in {hdir_name}, skipping")
                continue
            
            # hstack for background and histo for signal
            bkg_stack     = ROOT.THStack(f'bkg_{channel}_{hdir_name}', '')
            h_signal      = None
            legend_entries = []
            seen_samples  = set()
            for sample_key in hdir.GetListOfKeys():
                sample_name = sample_key.GetName()
                if sample_name not in used_mc_samples_names: continue
                if sample_name in seen_samples: continue
                seen_samples.add(sample_name)

                h = hdir.Get(sample_name).Clone(f'{hdir_name}_{sample_name}_sep')
                color = libsamples.colours.get(sample_name, ROOT.kGray + 1)

                if sample_name == 'bstautau':
                    h_signal = h
                    h_signal.SetLineColor(color)
                    h_signal.SetLineWidth(3)
                    h_signal.SetFillColor(0)
                    legend_entries.append((h_signal, sample_name + f"#times {signal_scale}", 'L'))
                else:
                    pu.set_histogram_style(h, hdir_name, 'events', color, color)
                    bkg_stack.Add(h)
                    legend_entries.append((h, sample_name, 'F'))

            if not h_signal or not bkg_stack.GetStack():
                print(f"    WARNING: missing signal or backgrounds for {hdir_name}, skipping")
                continue

            # S/sqrt(S+B) and S/sqrt(B) per bin
            bkg_total = bkg_stack.GetStack().Last()
            h_sep = h_signal.Clone(f'{hdir_name}_ssqrtsplusb')
            h_sep.Reset()
            h_sep_b = h_signal.Clone(f'{hdir_name}_ssqrtsb')
            h_sep_b.Reset()
            for ibin in range(1, h_signal.GetNbinsX() + 1):
                s = h_signal.GetBinContent(ibin)
                b = bkg_total.GetBinContent(ibin)
                #print(f"    Bin {ibin}: S={s:.2f}, B={b:.2f}, S/sqrt(S+B)={s/np.sqrt(s+b) if (s+b)>0 else 0:.4f}")
                val = s / np.sqrt(s + b) if (s + b) > 0 else 0
                err = val * np.sqrt((1/s if s > 0 else 0) + (1/(s+b) if (s+b) > 0 else 0)) if val > 0 else 0
                h_sep.SetBinContent(ibin, s / np.sqrt(s + b) if (s + b) > 0 else 0)
                h_sep.SetBinError(ibin, err)

                val_b = s / np.sqrt(b) if b > 0 else 0
                err_b = val_b * np.sqrt(1/s if s > 0 else 0) if val_b > 0 else 0
                h_sep_b.SetBinContent(ibin, val_b)
                h_sep_b.SetBinError(ibin, err_b)

            # canvas and drawing
            c = ROOT.TCanvas(f'c_{channel}_{hdir_name}', '', 1200, 800)
            c.cd()

            bkg_stack.Draw('hist')
            bkg_stack.GetXaxis().SetTitle(hdir_name)
            bkg_stack.GetYaxis().SetTitle('Events')

            ymax = max(bkg_stack.GetMaximum(), h_signal.GetMaximum())
            bkg_stack.SetMaximum(1.5 * ymax)

            stats = pu.draw_stat(bkg_stack)
            #scale signal x signal_scale for visibility
            h_signal.Scale(signal_scale)
            h_signal.Draw('hist same')

            leg = ROOT.TLegend(0.55, 0.65, 0.92, 0.90)
            leg.SetBorderSize(0)
            leg.SetFillStyle(0)
            leg.SetTextFont(42)
            leg.SetTextSize(0.030)
            leg.SetNColumns(2)
            for h_entry, label, opt in legend_entries:
                leg.AddEntry(h_entry, label, opt)
            leg.Draw('same')
            ch_label.DrawLatex(0.25, 0.80, channel_label.get(channel, channel))

            c.SaveAs(thisoutpath.format(ext='png'))
            c.SaveAs(thisoutpath.format(ext='pdf'))

            # S/sqrt(S+B) plot
            c_sep = ROOT.TCanvas(f'c_sep_{channel}_{hdir_name}', '', 1200, 800)
            c_sep.cd()
            h_sep.SetLineColor(ROOT.kRed + 1)
            h_sep.SetLineWidth(2)
            h_sep.GetXaxis().SetTitle(hdir_name)
            h_sep.GetYaxis().SetTitle('S/#sqrt{S+B}')
            h_sep.Draw('hist E')
            ch_label.DrawLatex(0.25, 0.80, channel_label.get(channel, channel))

            # S/sqrt(B) plot
            c_sep_b = ROOT.TCanvas(f'c_sep_b_{channel}_{hdir_name}', '', 1200, 800)
            c_sep_b.cd()
            h_sep_b.SetLineColor(ROOT.kBlue + 1)
            h_sep_b.SetLineWidth(2)
            h_sep_b.GetXaxis().SetTitle(hdir_name)
            h_sep_b.GetYaxis().SetTitle('S/#sqrt{B}')
            h_sep_b.Draw('hist E')
            ch_label.DrawLatex(0.25, 0.80, channel_label.get(channel, channel))

            c_sep.SaveAs(thisoutpath.format(ext='png').replace('.png', '_ssqrtsplusb.png'))
            c_sep.SaveAs(thisoutpath.format(ext='pdf').replace('.pdf', '_ssqrtsplusb.pdf'))
            c_sep_b.SaveAs(thisoutpath.format(ext='png').replace('.png', '_ssqrtb.png'))
            c_sep_b.SaveAs(thisoutpath.format(ext='pdf').replace('.pdf', '_ssqrtb.pdf'))

            # ROC curve: collect graph per channel, compare later
            if not 'sig_frac' in hdir_name: continue
            n_bins  = h_signal.GetNbinsX()
            s_total = h_signal.Integral(0, n_bins + 1)
            b_total = bkg_total.Integral(0, n_bins + 1)

            if s_total > 0 and b_total > 0:
                roc_sig_eff = []
                roc_bkg_rej = []
                for ibin in range(n_bins + 2, 0, -1):  # scan from high to low score
                    s_pass = h_signal.Integral(ibin, n_bins + 1)
                    b_pass = bkg_total.Integral(ibin, n_bins + 1)
                    roc_sig_eff.append(s_pass / s_total)
                    roc_bkg_rej.append(1.0 - b_pass / b_total)

                roc_x = np.array(roc_sig_eff, dtype=float)
                roc_y = np.array(roc_bkg_rej, dtype=float)

                g_roc = ROOT.TGraph(len(roc_x), roc_x, roc_y)
                g_roc.SetName(f'roc_{channel}_{hdir_name}')
                g_roc.SetTitle(channel_label.get(channel, channel))
                color = channel_colors.get(channel, ROOT.kGray + 1)
                g_roc.SetLineColor(color)
                g_roc.SetLineWidth(2)
                g_roc.SetMarkerStyle(20)
                g_roc.SetMarkerSize(0.3)
                g_roc.SetMarkerColor(color)
                roc_graphs.setdefault(hdir_name, {})[channel] = g_roc
            else:
                print(f"    WARNING: zero signal or background integral for {hdir_name}, skipping ROC")

    # -- ROC comparison: one canvas per hdir_name, all channels overlaid --
    roc_outpath = os.path.join(outdir, 'roc_curves.root')
    roc_file = ROOT.TFile(roc_outpath, 'RECREATE')

    for hdir_name, ch_graphs in roc_graphs.items():
        if not ch_graphs:
            continue

        mg = ROOT.TMultiGraph(f'mg_roc_{hdir_name}', '')
        leg_roc = ROOT.TLegend(0.25, 0.20, 0.50, 0.5)
        leg_roc.SetBorderSize(0)
        leg_roc.SetFillStyle(0)
        leg_roc.SetTextFont(42)
        leg_roc.SetTextSize(0.035)

        for channel in channels:
            g = ch_graphs.get(channel)
            if g is None:
                continue
            mg.Add(g, 'LP')
            leg_roc.AddEntry(g, channel_label.get(channel, channel), 'LP')
            roc_file.cd()
            g.Write()

        c_roc_cmp = ROOT.TCanvas(f'c_roc_cmp_{hdir_name}', '', 800, 800)
        c_roc_cmp.cd()
        mg.Draw('A')
        mg.GetXaxis().SetTitle('Signal efficiency')
        mg.GetYaxis().SetTitle('Background rejection (1 - #varepsilon_{B})')
        mg.GetXaxis().SetLimits(0, 1)
        mg.GetHistogram().SetMaximum(1)
        mg.GetHistogram().SetMinimum(0)
        leg_roc.Draw('same')

        cmp_base = os.path.join(outdir, f'{hdir_name}_roc_comparison')
        c_roc_cmp.SaveAs(cmp_base + '.png')
        c_roc_cmp.SaveAs(cmp_base + '.pdf')
        print(f"  > ROC comparison saved: {cmp_base}.png")

    roc_file.Close()
    print(f"\n ROC TGraphs written to {roc_outpath}")
