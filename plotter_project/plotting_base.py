import ROOT
from cmsstyle import CMS_lumi
from blinding_utils import apply_data_blinding_to_histogram, should_apply_blinding

class PlottingConfig:
    """Centralized configuration for all plotting operations."""
    
    # Canvas settings
    CANVAS_WIDTH = 700
    CANVAS_HEIGHT = 700
    
    # Legend settings
    LEGEND_COLUMNS = 3
    LEGEND_POSITION = (0.24, 0.67, 0.95, 0.90)
    
    # Plot styling
    Y_SCALE_FACTOR = 1.6
    LOG_SCALE_MULTIPLIER = 1000
    MINIMUM_Y = 0.0001
    
    # File formats
    SAVE_FORMATS = ['pdf', 'png', 'C', 'root']
    
    # ROOT file settings
    COMPRESSION_ALGO = ROOT.kLZMA
    COMPRESSION_LEVEL = 1

class PlottingBase:
    """Base class containing all common plotting functionality."""
    
    def __init__(self, config=None):
        self.config = config or PlottingConfig()
    
    def create_canvas_with_pads(self):
        """Create standardized canvas with main and ratio pads."""
        c1 = ROOT.TCanvas('c1', '', self.config.CANVAS_WIDTH, self.config.CANVAS_HEIGHT)
        c1.Draw()
        
        c1.cd()
        main_pad = ROOT.TPad('main_pad', '', 0., 0.25, 1., 1.)
        main_pad.Draw()
        main_pad.SetTicks(True)
        main_pad.SetBottomMargin(0.)
        
        c1.cd()
        ratio_pad = ROOT.TPad('ratio_pad', '', 0., 0., 1., 0.25)
        ratio_pad.Draw()
        ratio_pad.SetTopMargin(0.)
        ratio_pad.SetGridy()
        ratio_pad.SetBottomMargin(0.45)
        
        return c1, main_pad, ratio_pad
    
    def set_histogram_style(self, hist, x_title, y_title, fill_color, line_color):
        """Apply consistent styling to histograms."""
        hist.GetXaxis().SetTitle(x_title)
        hist.GetYaxis().SetTitle(y_title)
        hist.SetFillColor(fill_color)
        hist.SetLineColor(line_color)
    
    def create_base_legend(self):
        """Create legend with standard settings."""
        x1, y1, x2, y2 = self.config.LEGEND_POSITION
        leg = ROOT.TLegend(x1, y1, x2, y2)
        leg.SetBorderSize(0)
        leg.SetFillColor(0)
        leg.SetFillStyle(0)
        leg.SetTextFont(42)
        leg.SetTextSize(0.035)
        leg.SetNColumns(self.config.LEGEND_COLUMNS)
        return leg
    
    def draw_stat_uncertainty(self, stack):
        """Draw statistical uncertainty band."""
        if not (stack.GetStack() and stack.GetStack().Last()):
            return None
        
        stats = stack.GetStack().Last().Clone()
        stats.SetLineColor(0)
        stats.SetFillColor(ROOT.kGray + 1)
        stats.SetFillStyle(3344)
        stats.SetMarkerSize(0)
        stats.Draw('E2 SAME')
        return stats
    
    def calculate_plot_maximum(self, mc_max, data_max, bstautau_hist=None, reference_integral=None):
        """Calculate optimal plot maximum considering all components including BsTauTau scaling."""
        if not bstautau_hist:
            return self.config.Y_SCALE_FACTOR * max(mc_max, data_max)
        
        bstautau_unscaled_max = bstautau_hist.GetMaximum()
        
        if reference_integral and bstautau_hist.Integral() > 0:
            scale_factor = reference_integral / bstautau_hist.Integral()
            bstautau_scaled_max = bstautau_unscaled_max * scale_factor
        else:
            bstautau_scaled_max = bstautau_unscaled_max
        
        return self.config.Y_SCALE_FACTOR * max(mc_max, data_max, bstautau_unscaled_max, bstautau_scaled_max)
    
    def setup_drawing_frame(self, main_pad, x_min, x_max, y_max, x_title, y_title):
        """Setup drawing frame with fixed ranges."""
        main_pad.Clear()
        frame = main_pad.DrawFrame(x_min, self.config.MINIMUM_Y, x_max, y_max)
        frame.GetXaxis().SetTitle(x_title)
        frame.GetYaxis().SetTitle(y_title)
        return frame
    
    def style_and_draw_bstautau(self, bstautau_hist, colors, reference_stack=None, scale_to_mc=True):
        """Universal BsTauTau styling and drawing function."""
        if not bstautau_hist:
            return None
        
        # Handle both lazy RDataFrame objects and direct histograms
        if hasattr(bstautau_hist, 'GetValue'):
            hist = bstautau_hist.GetValue()
        else:
            hist = bstautau_hist
        
        hist.SetFillColor(0)
        hist.SetLineColor(colors['bstautau'])
        hist.SetMarkerColor(colors['bstautau'])
        
        # Note: This method would need access to data histogram for proper scaling
        # For now, keeping the original logic but this should be updated by the specific plotters
        if scale_to_mc and reference_stack and reference_stack.GetStack() and reference_stack.GetStack().Last():
            reference_integral = reference_stack.GetStack().Last().Integral()
            if hist.Integral() > 0:
                scale_factor = reference_integral / hist.Integral()
                hist.Scale(scale_factor)
        
        hist.Draw("hist same")
        hist.Draw("EP same")
        return hist
    
    def apply_data_blinding(self, hist, histogram_name, blinding_enabled):
        """Apply data blinding if conditions are met."""
        if should_apply_blinding(histogram_name) and blinding_enabled:
            apply_data_blinding_to_histogram(hist, histogram_name)
    
    def add_cms_label(self, pad):
        """Add standard CMS label."""
        CMS_lumi(pad, 4, 0, cmsText='CMS', extraText=' Preliminary', lumi_13TeV='L = 59.7 fb^{-1}')
    
    def save_plot_in_formats(self, canvas, base_path, filename, main_pad):
        """Save plot in linear and log versions with all formats."""
        # Linear version
        main_pad.SetLogy(False)
        canvas.Modified()
        canvas.Update()
        
        for fmt in self.config.SAVE_FORMATS:
            canvas.SaveAs(f'{base_path}/lin/{fmt}/{filename}.{fmt}')
        
        # Log version
        main_pad.SetLogy(True)
        current_max = self._get_pad_maximum(main_pad)
        log_max = current_max * self.config.LOG_SCALE_MULTIPLIER
        self._set_objects_maximum(main_pad, log_max)
        
        canvas.Modified()
        canvas.Update()
        
        for fmt in self.config.SAVE_FORMATS:
            canvas.SaveAs(f'{base_path}/log/{fmt}/{filename}.{fmt}')
        
        # Reset to linear
        main_pad.SetLogy(False)
        self._set_objects_maximum(main_pad, current_max)
        canvas.Modified()
        canvas.Update()
    
    def _get_pad_maximum(self, pad):
        """Extract maximum value from all drawable objects in pad."""
        current_max = 1
        for obj in pad.GetListOfPrimitives():
            if hasattr(obj, 'GetMaximum'):
                obj_max = obj.GetMaximum()
                if obj_max > current_max:
                    current_max = obj_max
            elif hasattr(obj, 'GetStack') and obj.GetStack():
                stack_max = obj.GetStack().Last().GetMaximum()
                if stack_max > current_max:
                    current_max = stack_max
        return current_max
    
    def _set_objects_maximum(self, pad, maximum):
        """Set maximum for all drawable objects in pad."""
        for obj in pad.GetListOfPrimitives():
            if hasattr(obj, 'SetMaximum'):
                obj.SetMaximum(maximum)
            if hasattr(obj, 'SetMinimum'):
                obj.SetMinimum(1e-1)
    
    def create_root_file(self, file_path):
        """Create ROOT file with standard compression settings."""
        root_file = ROOT.TFile(file_path, 'UPDATE', "", self.config.COMPRESSION_ALGO)
        root_file.SetCompressionLevel(self.config.COMPRESSION_LEVEL)
        return root_file
    
    def create_ratio_plot_elements(self, data_hist, stats_hist, ratio_pad):
        """Create ratio plot components."""
        ratio_pad.cd()
        
        ratio = data_hist.Clone()
        ratio.Divide(stats_hist)
        
        ratio_stats = stats_hist.Clone()
        ratio_stats.SetName(ratio.GetName() + '_ratiostats')
        ratio_stats.Divide(stats_hist)
        ratio_stats.SetMaximum(1.19999)
        ratio_stats.SetMinimum(0.79999)
        ratio_stats.GetYaxis().SetTitle('obs/exp')
        ratio_stats.GetYaxis().SetTitleOffset(0.5)
        ratio_stats.GetYaxis().SetNdivisions(405)
        
        # Scale axis labels for ratio pad
        ratio_stats.GetXaxis().SetLabelSize(3.0 * ratio.GetXaxis().GetLabelSize())
        ratio_stats.GetYaxis().SetLabelSize(3.0 * ratio.GetYaxis().GetLabelSize())
        ratio_stats.GetXaxis().SetTitleSize(3.0 * ratio.GetXaxis().GetTitleSize())
        ratio_stats.GetYaxis().SetTitleSize(3.0 * ratio.GetYaxis().GetTitleSize())
        
        line = ROOT.TLine(ratio.GetXaxis().GetXmin(), 1., ratio.GetXaxis().GetXmax(), 1.)
        line.SetLineColor(ROOT.kBlack)
        line.SetLineWidth(1)
        
        return ratio, ratio_stats, line
