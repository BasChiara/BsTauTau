#def define_total_weight(sample, k, files_names, options):
#    """
#    Defines the total event weight for a given sample.
#
#    Args:
#        sample: The RDataFrame containing the sample data.
#        k (str): Sample key.
#        files_names (dict): Mapping of sample keys to filenames.
#        options (dict): Dict of flags like compute_sfs, use_ntuples_with_sfs, etc.
#
#    Returns:
#        Updated RDataFrame with a new column 'total_weight'.
#    """
#    weight_list = build_weight_string(k, files_names, options).split('*')
#    sample      = sf_cpp.combine_insert_weight(sample, 'tot_weight', weight_list, make_variations=True, debug=True)
#
#    return sample