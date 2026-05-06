import ROOT
import math
from datetime import datetime
from cmsstyle import CMS_lumi
from officialStyle import officialStyle
from blinding_utils import apply_data_blinding_to_histogram, should_apply_blinding

officialStyle(ROOT.gStyle, ROOT.TGaxis)


def create_canvas_with_pads():
    """
    Creates a ROOT canvas with two pads: a main pad and a ratio pad.
    
    Returns:
        tuple: A tuple containing the canvas, main pad, and ratio pad.
    """
    # Create the canvas
    c1 = ROOT.TCanvas('c1', '', 700, 700)
    c1.Draw()
    
    # Create the main pad
    c1.cd()
    main_pad = ROOT.TPad('main_pad', '', 0., 0.25, 1., 1.)
    main_pad.Draw()
    main_pad.SetTicks(True)
    main_pad.SetBottomMargin(0.)
    
    # Create the ratio pad
    c1.cd()
    ratio_pad = ROOT.TPad('ratio_pad', '', 0., 0., 1., 0.25)
    ratio_pad.Draw()
    ratio_pad.SetTopMargin(0.)
    ratio_pad.SetGridy()
    ratio_pad.SetBottomMargin(0.45)
    
    return c1, main_pad, ratio_pad

def initialize_histograms(histos, samples, ch):
    temp_hists = {}
    
    for k, v in histos[ch].items():
        temp_hists[k] = {}
        for kk, vv in samples[ch].items():
            branch_name = k
            temp_hists[k][f'{k}_{kk}'] = vv.Histo1D(v[0], branch_name, 'tot_weight')
            
            # stat + systematic error
            if 'data' in kk: continue
            tmp_histUp   = vv.Histo1D(v[0], branch_name, 'tot_weightUp')
            tmp_histDown = vv.Histo1D(v[0], branch_name, 'tot_weightDown')
            for ibin in range(temp_hists[k][f'{k}_{kk}'].GetNbinsX()):
                
                ths_sys  = 0.5*abs(tmp_histUp.GetBinContent(ibin+1) - tmp_histDown.GetBinContent(ibin+1)) 
                ths_stat = temp_hists[k][f'{k}_{kk}'].GetBinError(ibin+1)
                ths_err = math.sqrt(ths_stat**2 + ths_sys**2)
                
                #print(f'\t\t\t{ibin+1} {temp_hists[k][f'{k}_{kk}'].GetBinContent(ibin+1):.3f} +/- {ths_sys:.3f} (sys) +/- {ths_stat:.3f} (stat)')
                if math.isnan(ths_err): print('WARNING - nan in the error')
                temp_hists[k][f'{k}_{kk}'].SetBinError(ibin+1, ths_err )
            
            tmp_histUp.Clear()
            tmp_histDown.Clear()
    return temp_hists


def set_histogram_style(hist, x_title, y_title, fill_color, line_color):
    hist.GetXaxis().SetTitle(x_title)
    hist.GetYaxis().SetTitle(y_title)
    hist.SetFillColor(fill_color)
    hist.SetLineColor(line_color)

def create_legend(temp_hists, samples_for_legend, titles):
    leg = ROOT.TLegend(0.24,.67,.95,.90)
    leg.SetBorderSize(0)
    leg.SetFillColor(0)
    leg.SetFillStyle(0)
    leg.SetTextFont(42)
    leg.SetTextSize(0.035)
    leg.SetNColumns(3)
    k = list(temp_hists.keys())[0]
    for kk in samples_for_legend:
        leg.AddEntry(temp_hists[k]['%s_%s' %(k, kk)].GetValue(), titles[kk], 'EP' if 'data' in kk else ('L' if 'bstautau' in kk else 'F'))

    return leg

def compute_ratio_plot(temp_hists, ratio, stats, ratio_pad):
    ratio_pad.cd()
    ratio_stats = stats.Clone()
    ratio_stats.SetName(ratio.GetName()+'_ratiostats')
    ratio_stats.Divide(stats)
    ratio_stats.SetMaximum(1.19999) # avoid displaying 2, that overlaps with 0 in the main_pad
    ratio_stats.SetMinimum(0.79999) # and this is for symmetry
    ratio_stats.GetYaxis().SetTitle('obs/exp')
    ratio_stats.GetYaxis().SetTitleOffset(0.5)
    ratio_stats.GetYaxis().SetNdivisions(405)
    ratio_stats.GetXaxis().SetLabelSize(3.* ratio.GetXaxis().GetLabelSize())
    ratio_stats.GetYaxis().SetLabelSize(3.* ratio.GetYaxis().GetLabelSize())
    ratio_stats.GetXaxis().SetTitleSize(3.* ratio.GetXaxis().GetTitleSize())
    ratio_stats.GetYaxis().SetTitleSize(3.* ratio.GetYaxis().GetTitleSize())
    
    norm_stack = ROOT.THStack('norm_stack', '')
    
    for kk, vv in temp_hists.items():
        if 'data' in kk: continue
        hh = vv.Clone()
        hh.Divide(stats)



    line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1., ratio.GetXaxis().GetXmax(), 1.)
    line.SetLineColor(ROOT.kBlack)
    line.SetLineWidth(1)
 
    return ratio_stats, norm_stack,line, ratio


def get_data_sample_name(ch):
    return 'data_sm' if ch in ['emu', 'mumu', 'mu'] else 'data_eg'


def get_samples_for_legend(samples, ch, data_smpl):
    return [str(k) for k in samples[ch] if 'data' not in k and 'ext' not in k] + [data_smpl]


def style_histograms(temp_hists, k, v, colours):
    for key, ihist in temp_hists[k].items():
        sample_name = key.split(k + '_')[1]
        is_data = f'{k}_data' in key
        color = ROOT.kWhite if is_data else colours.get(sample_name, ROOT.kBlack)
        set_histogram_style(ihist, v[1], 'events', color, color)


def create_histogram_stacks(temp_hists, k, blinding):
    """Creates histogram stacks for the given channel, both data and MC."""
    ths1 = ROOT.THStack('stack', '')
    data_ths = ROOT.THStack('data_stack', '')

    for key, ihist in temp_hists[k].items():
        if f'{k}_data' in key:
            continue
        ihist.Draw('hist same')
        if "bstautau" not in key:
            ths1.Add(ihist.GetValue())

    ths1.SetMinimum(0.0001)

    for key, ihist in temp_hists[k].items():
        if f'{k}_data' not in key:
            continue
        
        # CRITICAL: Clone the histogram for display only - don't modify the original
        display_hist = ihist.GetValue().Clone(f"{key}_display")
        
        
        # Apply blinding ONLY to the display clone, not the original
        if should_apply_blinding(k) and blinding:
            apply_data_blinding_to_histogram(display_hist, k)
        
        display_hist.Draw('hist same')
        display_hist.SetLineWidth(0)
        data_ths.Add(display_hist)  # Use the cloned version for display


    return ths1, data_ths


def draw_stat(ths1):

    stats = ths1.GetStack().Last().Clone()
    stats.SetLineColor(0)
    stats.SetFillColor(ROOT.kGray + 1)
    stats.SetFillStyle(3344)
    stats.SetMarkerSize(0)
    stats.Draw('E2 SAME')

    return stats


def style_and_draw_bstautau(temp_hists, k, ths1, colours, scale_to_mc=True):
    hist = temp_hists[k][f'{k}_bstautau']
    hist.SetFillColor(0)
    hist.SetMarkerSize(0)
    hist.SetLineColor(colours['bstautau'])
    hist.SetMarkerColor(colours['bstautau'])
    #print("BsTauTau histogram integral:", hist.Integral(),k)
    
    if scale_to_mc:
        # Scale to MC stack (ths1) instead of data
        if ths1.GetStack() and ths1.GetStack().Last() and hist.Integral() > 0:
            mc_integral = ths1.GetStack().Last().Integral()
            scale_factor = mc_integral / hist.Integral()
            hist.Scale(scale_factor)
            #print(f"Scaled BsTauTau histogram to MC for total of {hist.Integral()}")

    hist.Draw("hist same")
    hist.Draw("EP same")


def save_plot_versions(c1, label, ch, k, main_pad, scale_suffix=""):
    """
    Save plots in multiple formats and versions with new directory structure.
    """
    if scale_suffix == "_scaled":
        base_path = f'plots/{label}/{ch}/samples_based/bstautau_scaled'
    elif scale_suffix == "_unscaled":
        base_path = f'plots/{label}/{ch}/samples_based/bstautau_not_scaled'
    else:
        # For plots without BsTauTau, use scaled path as default
        base_path = f'plots/{label}/{ch}/samples_based/bstautau_scaled'
    
    # Linear version
    main_pad.SetLogy(False)
    c1.Modified()
    c1.Update()
    
    # Save linear versions in all formats
    c1.SaveAs(f'{base_path}/lin/pdf/{k}.pdf')
    c1.SaveAs(f'{base_path}/lin/png/{k}.png')
    c1.SaveAs(f'{base_path}/lin/C/{k}.C')
    c1.SaveAs(f'{base_path}/lin/root/{k}.root')
    
    # Log version - simplified maximum finding
    main_pad.SetLogy(True)
    
    # Get maximum more efficiently
    current_max = 1  # Default fallback
    pad_primitives = main_pad.GetListOfPrimitives()
    for obj in pad_primitives:
        if hasattr(obj, 'GetMaximum'):
            obj_max = obj.GetMaximum()
            if obj_max > current_max:
                current_max = obj_max
        elif hasattr(obj, 'GetStack') and obj.GetStack():
            stack_max = obj.GetStack().Last().GetMaximum()
            if stack_max > current_max:
                current_max = stack_max
    
    # Set maximum for log scale
    log_max = current_max * 1000
    for obj in pad_primitives:
        if hasattr(obj, 'SetMaximum'):
            obj.SetMaximum(log_max)
    
    c1.Modified()
    c1.Update()
    
    # Save log versions in all formats
    c1.SaveAs(f'{base_path}/log/pdf/{k}.pdf')
    c1.SaveAs(f'{base_path}/log/png/{k}.png')
    c1.SaveAs(f'{base_path}/log/C/{k}.C')
    c1.SaveAs(f'{base_path}/log/root/{k}.root')
    
    # Reset to linear and restore original maximum
    main_pad.SetLogy(False)
    for obj in pad_primitives:
        if hasattr(obj, 'SetMaximum'):
            obj.SetMaximum(current_max)
    c1.Modified()
    c1.Update()


def process_histograms(histos, temp_hists, samples, ch, colours, label, titles, main_pad, ratio_pad, c1, blinding):
    # Create ROOT file for saving histograms with compression
    root_file_path = f'plots/{label}/histograms.root'
    root_file = ROOT.TFile(root_file_path, 'UPDATE', "", ROOT.kLZMA)  # Use LZMA compression
    root_file.SetCompressionLevel(1)  # Fast compression
    print(f"Created ROOT file: {root_file_path}")
    
    # Create channel folder in ROOT file
    channel_folder = root_file.mkdir(ch)
    
    for i, (k, v) in enumerate(histos[ch].items()):
        c1.cd()
        data_smpl = get_data_sample_name(ch)
        samples_for_legend = get_samples_for_legend(samples, ch, data_smpl)
        leg = create_legend(temp_hists, samples_for_legend, titles)

        ## plotting main pad
        main_pad.cd()
        main_pad.SetLogy(False)

        style_histograms(temp_hists, k, v, colours)
        
        # Create histogram stacks
        ths1, data_ths = create_histogram_stacks(temp_hists, k, blinding)

        # Draw histogram first to get proper axis ranges
        ths1.Draw('hist')
        
        # Calculate desired maximum for Y-axis range (considering all scenarios)
        if ths1.GetStack() and ths1.GetStack().Last():
            mc_max = ths1.GetStack().Last().GetMaximum()
        else:
            mc_max = 1
            
        if data_ths.GetStack() and data_ths.GetStack().Last():
            data_max = data_ths.GetStack().Last().GetMaximum()
        else:
            data_max = 1
        
        # For BsTauTau plots, calculate max considering both scaled and unscaled versions
        if f'{k}_bstautau' in temp_hists[k]:
            bstautau_hist = temp_hists[k][f'{k}_bstautau'].GetValue()
            bstautau_unscaled_max = bstautau_hist.GetMaximum()
            
            # Calculate what the scaled max would be using MC INTEGRAL (back to original)
            if ths1.GetStack() and ths1.GetStack().Last():
                mc_integral = ths1.GetStack().Last().Integral()
                scale_factor = mc_integral / bstautau_hist.Integral() if bstautau_hist.Integral() > 0 else 1
                bstautau_scaled_max = bstautau_unscaled_max * scale_factor
            else:
                bstautau_scaled_max = bstautau_unscaled_max
            
            # Use the maximum of all scenarios
            desired_max = 1.5 * max(mc_max, data_max, bstautau_unscaled_max, bstautau_scaled_max)
        else:
            desired_max = 1.5 * max(mc_max, data_max)
        
        # Get X-axis range from the histogram
        x_min = ths1.GetXaxis().GetXmin()
        x_max = ths1.GetXaxis().GetXmax()
        
        # Clear and redraw with fixed Y-axis range
        main_pad.Clear()
        
        # Draw frame with desired Y-axis range
        frame = main_pad.DrawFrame(x_min, 0.0001, x_max, desired_max)
        frame.GetXaxis().SetTitle(v[1])
        frame.GetYaxis().SetTitle('events')
        
        # Draw histogram on top of the fixed frame
        ths1.Draw('hist same')

        stats = draw_stat(ths1)
        data_ths.GetStack().Last().SetLineColor(ROOT.kBlack)
        data_ths.GetStack().Last().Draw('EP same')

        # Print data integral for debugging/verification
        if data_ths.GetStack() and data_ths.GetStack().Last():
            data_integral = data_ths.GetStack().Last().Integral()
            #print(f"Data histogram integral for {k}: {data_integral:.1f}")

        #leg.AddEntry(stats, 'stat. unc.', 'F')
        leg.AddEntry(stats, 'tot. unc.', 'F')
        leg.Draw('same')

        # CRITICAL: Save histograms to ROOT file BEFORE any scaling to preserve original integrals
        save_histograms_to_root_file(channel_folder, k, ths1, data_ths, temp_hists)

        # IMPORTANT: Plot unscaled version FIRST, then scaled version
        # because scaling modifies the histogram permanently
        
        # Version 1: BsTauTau at original scale (not scaled to MC) - PLOT FIRST
        if f'{k}_bstautau' in temp_hists[k].keys():
            style_and_draw_bstautau(temp_hists, k, ths1, colours, scale_to_mc=False)

        CMS_lumi(main_pad, 4, 0, cmsText='CMS', extraText=' Preliminary', lumi_13TeV='L = 59.7 fb^{-1}')
        main_pad.cd()

        ratio = data_ths.GetStack().Last().Clone()
        ratio.Divide(stats)

        ratio_stats, norm_stack, line, ratio = compute_ratio_plot(temp_hists[k], ratio, stats, ratio_pad)
        ratio_pad.cd()

        norm_stack.Draw('hist same')
        ratio_stats.Draw('E2')
        norm_stack.Draw('hist same')
        ratio_stats.Draw('E2 same')
        line.Draw('same')
        ratio.Draw('EP same')

        # Save unscaled version in all formats (linear and log)
        save_plot_versions(c1, label, ch, k, main_pad, scale_suffix="_unscaled")

        # Version 2: BsTauTau scaled to data (current behavior) - PLOT SECOND
        if f'{k}_bstautau' in temp_hists[k].keys():
            # Clear and redraw everything with scaling
            c1.cd()
            main_pad.cd()
            main_pad.Clear()
            
            # Apply the same frame strategy for the scaled version
            frame = main_pad.DrawFrame(x_min, 0.0001, x_max, desired_max)
            frame.GetXaxis().SetTitle(v[1])
            frame.GetYaxis().SetTitle('events')
            
            # Redraw the main plot components on the fixed frame
            ths1.Draw('hist same')
            stats.Draw('E2 SAME')
            data_ths.GetStack().Last().Draw('EP same')
            leg.Draw('same')
            
            # Draw BsTauTau WITH scaling (this will modify the histogram permanently)
            style_and_draw_bstautau(temp_hists, k, ths1, colours, scale_to_mc=True)
            
            CMS_lumi(main_pad, 4, 0, cmsText='CMS', extraText=' Preliminary', lumi_13TeV='L = 59.7 fb^{-1}')
            
            # Redraw ratio plot (same as before)
            ratio_pad.cd()
            ratio_pad.Clear()
            norm_stack.Draw('hist same')
            ratio_stats.Draw('E2')
            norm_stack.Draw('hist same')
            ratio_stats.Draw('E2 same')
            line.Draw('same')
            ratio.Draw('EP same')
            
            # Save scaled version in all formats (linear and log)
            save_plot_versions(c1, label, ch, k, main_pad, scale_suffix="_scaled")

        else:
            # For plots without BsTauTau, just save the regular version
            save_plot_versions(c1, label, ch, k, main_pad, scale_suffix="")

        # ROOT file already saved above before any scaling

    # Close the ROOT file

def save_histograms_to_root_file(channel_folder, histogram_name, ths1, data_ths, temp_hists):
    """
    Save histograms to ROOT file with proper folder structure matching plot organization.
    CRITICAL: Always saves ORIGINAL UNBLINDED data for fitting purposes.
    """
    # Create main histogram folder
    histo_folder = channel_folder.mkdir(histogram_name)
    
    # Create subfolders for different versions
    bstautau_scaled_folder = histo_folder.mkdir("bstautau_scaled")
    lin_scaled_folder = bstautau_scaled_folder.mkdir("lin")
    log_scaled_folder = bstautau_scaled_folder.mkdir("log")
    
    # Only create unscaled folders if bstautau is present
    if f'{histogram_name}_bstautau' in temp_hists[histogram_name]:
        bstautau_unscaled_folder = histo_folder.mkdir("bstautau_not_scaled")
        lin_unscaled_folder = bstautau_unscaled_folder.mkdir("lin")
        log_unscaled_folder = bstautau_unscaled_folder.mkdir("log")
    else:
        # Create empty unscaled folders for consistency
        bstautau_unscaled_folder = histo_folder.mkdir("bstautau_not_scaled")
        lin_unscaled_folder = bstautau_unscaled_folder.mkdir("lin")
        log_unscaled_folder = bstautau_unscaled_folder.mkdir("log")
   
    # Function to save histograms in a specific folder
    def save_histos_in_folder(folder, bstautau_scaled=True):
        folder.cd()
        
        # Save MC stack (total background)
        if ths1.GetStack() and ths1.GetStack().Last():
            mc_total = ths1.GetStack().Last().Clone(f"{histogram_name}_mc_total")
            mc_total.Write("mc_total")
        
        # CRITICAL: Save the ACTUAL plotted data from data_ths (before blinding was applied)
        if data_ths.GetStack() and data_ths.GetStack().Last():
            # Get the original data from temp_hists first (unblinded)
            original_data_hist = None
            
            original_data_hist = data_ths.GetStack().Last().Clone(f"{histogram_name}_data_original")
            
            if original_data_hist:
                original_data_hist.Write("data_obs")  # Use ROOT-friendly name for fitting
            else:
                print(f"WARNING: No original data histogram found for {histogram_name}")
        
        # Save bstautau signal if present
        if f'{histogram_name}_bstautau' in temp_hists[histogram_name]:
            # CRITICAL: Always clone the original histogram first to avoid permanent modification
            original_bstautau = temp_hists[histogram_name][f'{histogram_name}_bstautau'].GetValue()
            bstautau_hist = original_bstautau.Clone(f"{histogram_name}_bstautau_{'scaled' if bstautau_scaled else 'unscaled'}")
            
            # Apply scaling to MC instead of data if this is the scaled version
            if bstautau_scaled and ths1.GetStack() and ths1.GetStack().Last():
                mc_integral = ths1.GetStack().Last().Integral()
                if bstautau_hist.Integral() > 0:
                    scale_factor = mc_integral / bstautau_hist.Integral()
                    bstautau_hist.Scale(scale_factor)
            
            bstautau_hist.Write("bstautau")
        
        # Save individual MC samples
        for key, ihist in temp_hists[histogram_name].items():
            sample_name = key.split(f'{histogram_name}_')[1]
            
            # Skip data and bstautau (already saved separately)
            if 'data' in sample_name or 'bstautau' in sample_name:
                continue
                
            # Clone and save individual MC samples
            individual_hist = ihist.GetValue().Clone(f"{histogram_name}_{sample_name}")
            individual_hist.Write(sample_name)
    
    # Save scaled versions (both linear and log - same histograms, different organization)
    save_histos_in_folder(lin_scaled_folder, bstautau_scaled=True)
    save_histos_in_folder(log_scaled_folder, bstautau_scaled=True)
    
    # Save unscaled versions only if bstautau is present
    if f'{histogram_name}_bstautau' in temp_hists[histogram_name]:
        save_histos_in_folder(lin_unscaled_folder, bstautau_scaled=False)
        save_histos_in_folder(log_unscaled_folder, bstautau_scaled=False)
    
    # Save unscaled versions only if bstautau is present
    if f'{histogram_name}_bstautau' in temp_hists[histogram_name]:
        save_histos_in_folder(lin_unscaled_folder, bstautau_scaled=False)
        save_histos_in_folder(log_unscaled_folder, bstautau_scaled=False)
