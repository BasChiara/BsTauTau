import ROOT

def get_genEventSumw(file_path):
    """Retrieve the sum of genEventSumw from the Runs tree in a ROOT file."""
    f = ROOT.TFile.Open(file_path)
    runs_tree = f.Get("Runs")
    if not runs_tree:
        raise RuntimeError(f"No Runs tree found in file {file_path}")

    sumw = 0
    for entry in runs_tree:
        sumw += entry.genEventSumw

    print(" [weight] the total enEventSumw is ",sumw)
    f.Close()
    return sumw
