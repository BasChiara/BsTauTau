def var(score): return f"btagged_loose_jets_pt_above_20_for_histo_{score}"

def sum_expr(scores): return " + ".join([var(s) for s in scores])

def define_combined_scores(
    samples,
    tau_scores,
    parT_scores,
    bkg_scores,
    is_bstautau,
    bstautau_masks=None,
):

    
    sig_sum = sum_expr(tau_scores)
    total_sum = sum_expr(parT_scores)
    bkg_sum = sum_expr(bkg_scores)

    # Define score sums
    samples = samples.Define(f"btagged_loose_jets_pt_above_20_for_histo_part_sig_sum", sig_sum)
    samples = samples.Define(f"btagged_loose_jets_pt_above_20_for_histo_part_total_sum", total_sum)
    samples = samples.Define(f"btagged_loose_jets_pt_above_20_for_histo_part_bkg_sum", bkg_sum)

    # Define all signals vs all bkgs
    sig_frac_var = f"btagged_loose_jets_pt_above_20_for_histo_part_all_sig_frac"
    samples = samples.Define(sig_frac_var, f"btagged_loose_jets_pt_above_20_for_histo_part_sig_sum / btagged_loose_jets_pt_above_20_for_histo_part_total_sum")

    # Define per-tau fraction and masked histograms for bstautau
    for tau in tau_scores:
        tau_var = var(tau)
        frac_var = f"{tau_var}_frac"
        frac_expr = f"{tau_var} / ({tau_var} + btagged_loose_jets_pt_above_20_for_histo_part_bkg_sum)"
        samples = samples.Define(frac_var, frac_expr) # define just the fraction (no mask on bstautau)

        # Apply decay-mode-specific mask if bstautau and masks provided
        if is_bstautau:
            decay_mode = tau.lower().replace("partraw", "")  # crude but works
            mask = bstautau_masks.get(decay_mode)
            expr_masked = f"{frac_var}[{mask}]" 
            expr_general = f"{frac_var}"  # General mask already used in the original branch definition
        else:
            expr_masked = frac_var
            expr_general = frac_var
        
        masked_var = f"{frac_var}_masked" # decay-mode specific for bstautau
        samples = samples.Define(masked_var, expr_masked)
        
        
        general_var = f"{frac_var}_general" # general mask for bstautau (no decay mode diversification)
        samples = samples.Define(general_var, expr_general)
        



    # Signal over individual background scores
    for bkg in bkg_scores:
        bkg_var = var(bkg)
        ratio_var = f"btagged_loose_jets_pt_above_20_for_histo_part_sig_over_{bkg}"
        expr = f"btagged_loose_jets_pt_above_20_for_histo_part_sig_sum / (btagged_loose_jets_pt_above_20_for_histo_part_sig_sum + {bkg_var})"
        samples = samples.Define(ratio_var, expr)


    return samples

def define_max_scores(
    samples,
    parT_scores,
    is_bstautau,
    bstautau_conditions=None
):
    """
    Define max score categorization for ParT scores.
    For each jet, determine which ParT score is maximum and create separate histograms.
    """

    # Create a combined matrix of all ParT scores for vectorized operations
    score_vars = [var(score) for score in parT_scores]
    
    # Define which score is maximum for each jet
    samples = samples.Define("part_scores_matrix", f"ROOT::RVec<ROOT::RVec<double>>{{{', '.join(score_vars)}}}")
    
    # Find the index of maximum score for each jet
    # Find the index of the maximum score for each jet, using part_scores_matrix
    samples = samples.Define("max_score_indices", """
        ROOT::VecOps::RVec<int> indices;
        auto& scores_matrix = part_scores_matrix;
        if (scores_matrix.size() > 0) {
            for (size_t i = 0; i < scores_matrix[0].size(); ++i) { // loop over jets
                double max_val = -1.0;
                int max_idx = 0;
                for (size_t j = 0; j < scores_matrix.size(); ++j) { // loop over ParT scores
                    double val = scores_matrix[j][i];
                    if (val > max_val) {
                        max_val = val;
                        max_idx = j;
                    }
                }
                indices.push_back(max_idx);
            }
        }
        return indices;
    """)
    
    # For each ParT score, create masks and corresponding histograms
    for i, score in enumerate(parT_scores):
        score_name = score.replace("ParTRaw", "").lower()
        
        # Create mask for jets where this score is maximum
        mask_var = f"max_{score_name}_mask" #1 if we save the jet, 0 if we don't save the jet
        samples = samples.Define(mask_var, f"max_score_indices == {i}")

        # Define the raw max score values for jets where this score is max
        raw_score_var = f"max_{score_name}_raw_score"
        raw_expr = f"{var(score)}[{mask_var}]"
        
        # If the score is a signal, ratio = signal / (signal+sum of bkg); if bkg, ratio = bkg / (bkg+sum of signal)
        signal_scores = [s for s in parT_scores if "tauh" in s.lower()]
        bkg_scores = [s for s in parT_scores if "tauh" not in s.lower()]
        is_signal = score in signal_scores
        if is_signal:
            numerator = var(score)
            denominator = " + ".join([var(s) for s in bkg_scores] + [var(score)])
        else:
            numerator = var(score)
            denominator = " + ".join([var(s) for s in signal_scores] + [var(score)])
        ratio_var = f"max_{score_name}_ratio"
        ratio_expr = f"({numerator} / ({denominator}))[{mask_var}]"
        
        # Apply bstautau mask for bstautau sample 
        if is_bstautau and bstautau_conditions:
            # For bstautau, apply the corresponding mask for each score
            bstautau_mask = bstautau_conditions.get(score_name)
            if bstautau_mask is not None:
                # Combine both masks: mask_var and bstautau_mask
                # This assumes both are boolean masks of the same length
                combined_mask = f"({mask_var} && {bstautau_mask})"
                raw_expr_masked = f"{var(score)}[{combined_mask}]"
                ratio_expr_masked = f"({numerator} / ({denominator}))[{combined_mask}]"

            else:
                # If no mask found, mask out all events (select zero events)
                raw_expr_masked = f"{var(score)}[false]"
                ratio_expr_masked = f"({numerator} / ({denominator}))[false]"

            samples = samples.Define(f"btagged_loose_jets_pt_above_20_{raw_score_var}_masked", raw_expr_masked)
            samples = samples.Define(f"btagged_loose_jets_pt_above_20_{ratio_var}_masked", ratio_expr_masked)
        else:
            samples = samples.Define(f"btagged_loose_jets_pt_above_20_{raw_score_var}_masked", raw_expr)
            samples = samples.Define(f"btagged_loose_jets_pt_above_20_{ratio_var}_masked", ratio_expr)

    return samples



def apply_part_sequential_cuts_filter(samples, is_bstautau=False):
    """Apply sequential cuts filter to create two sets of categories:
    
    1. EXCLUSIVE categories (refined cuts):
       - tauhtaumu: tauhtaumu > 0.6 (exclusive)
       - tauhtaue: tauhtaumu < 0.6 AND tauhtaue > 0.4 (exclusive)  
       - tauhtauh: tauhtaumu < 0.6 AND tauhtaue < 0.4 (exclusive)
    
    2. ONLYTAUMUCUT categories (simple cuts):
       - tauhtaumu: tauhtaumu > 0.6 
       - tauhtaue: tauhtaumu < 0.6
       - tauhtauh: tauhtaumu < 0.6
    """
    # Define cut conditions using GENERAL branches
    cut_variable_mu = "btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtaumu_frac_general"
    cut_variable_e = "btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtaue_frac_general"
    cut_threshold_mu = 0.6
    cut_threshold_e = 0.4

    # Define the cut conditions once
    cut_conditions = {
        'exclusive': {
            'tauhtaumu': f"{cut_variable_mu} > {cut_threshold_mu}",
            'tauhtaue': f"({cut_variable_mu} < {cut_threshold_mu}) && ({cut_variable_e} > {cut_threshold_e})",
            'tauhtauh': f"({cut_variable_mu} < {cut_threshold_mu}) && ({cut_variable_e} < {cut_threshold_e})"
        },
        'onlytaumucut': {
            'tauhtaumu': f"{cut_variable_mu} > {cut_threshold_mu}",
            'tauhtaue': f"{cut_variable_mu} < {cut_threshold_mu}",
            'tauhtauh': f"{cut_variable_mu} < {cut_threshold_mu}"
        }
    }

    branches_to_filter = [
        'btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtaue_frac_general',
        'btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtauh_frac_general', 
        'btagged_loose_jets_pt_above_20_for_histo_ParTRawTauhtaumu_frac_general'
    ]

    # Apply cuts to ParT score branches
    for branch_name in branches_to_filter:
        # Determine which tau type this branch represents
        if "Tauhtaumu" in branch_name:
            tau_type = 'tauhtaumu'
        elif "Tauhtaue" in branch_name:
            tau_type = 'tauhtaue'
        elif "Tauhtauh" in branch_name:
            tau_type = 'tauhtauh'
        else:
            continue
        
        # Apply cuts for both selection types
        for selection_type in ['exclusive', 'onlytaumucut']:
            condition = cut_conditions[selection_type][tau_type]
            filtered_branch = f"{branch_name}_{selection_type}"
            samples = samples.Define(filtered_branch, f"{branch_name}[{condition}]")

    # CRITICAL: Create hadronFlavour branches for EACH selection type and tau category
    hadron_flavour_base = 'btagged_loose_jets_pt_above_20_for_histo_hadronFlavour'
    
    for selection_type in ['exclusive', 'onlytaumucut']:
        for tau_type in ['tauhtaumu', 'tauhtaue', 'tauhtauh']:
            condition = cut_conditions[selection_type][tau_type]
            flavour_branch = f"{hadron_flavour_base}_{selection_type}_{tau_type}"
            samples = samples.Define(flavour_branch, f"{hadron_flavour_base}[{condition}]")
    
    # Also create general selection-type branches (not tau-specific) for convenience
    for selection_type in ['exclusive', 'onlytaumucut']:
        # Use tauhtaumu condition as default for general case
        general_condition = cut_conditions[selection_type]['tauhtaumu']
        general_flavour_branch = f"{hadron_flavour_base}_{selection_type}"
        samples = samples.Define(general_flavour_branch, f"{hadron_flavour_base}[{general_condition}]")


    # Jet mass branch base name
    jet_mass_base = "btagged_loose_jets_pt_above_20_for_histo_m"

    # Define jet mass branches for each exclusive selection
    samples = samples.Define(f"{jet_mass_base}_exclusive_tauhtaumu", f"{jet_mass_base}[{cut_conditions['exclusive']['tauhtaumu']}]")
    samples = samples.Define(f"{jet_mass_base}_exclusive_tauhtaue", f"{jet_mass_base}[{cut_conditions['exclusive']['tauhtaue']}]")
    samples = samples.Define(f"{jet_mass_base}_exclusive_tauhtauh", f"{jet_mass_base}[{cut_conditions['exclusive']['tauhtauh']}]")

    return samples

