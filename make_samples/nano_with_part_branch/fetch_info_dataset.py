"""
    Fetch dataset files and total events from DAS for a given dataset path or a list of dataset names specified in a YAML file.
    Usage:
        python fetch_info_dataset.py --dataset_yml <path_to_yaml> --dataset_keys <dataset_name1> <dataset_name2> ...
        python fetch_info_dataset.py --central_dataset <dataset_path>
"""

import os, sys
import subprocess
import yaml
import argparse

MAXCRABFILES = 10000

def get_arguments():
    parser = argparse.ArgumentParser(description="Fetch dataset files and total events from DAS.")
    parser.add_argument("--dataset_yml", 
                        type=str, 
                        help="Path to the YAML file containing dataset information.")
    parser.add_argument("--dataset_keys", 
                        type=str, nargs='+',
                        help="The key of the dataset to fetch from the YAML file. Can be a single name or a list of names. Use * to fetch all datasets.")
    parser.add_argument("--central_dataset",
                        type=str, 
                        help="Single dataset path in DAS. Overrides the dataset path in the YAML file if provided.")
    
    return parser.parse_args()

def get_info(dataset_path):
    """Query DAS to get the total number of events in a dataset."""
    query = f"dasgoclient -query='summary dataset={dataset_path}'"
    fieldstosave = ["nevent", "nfiles"]
    summary = {}
    try:
        result = subprocess.run(query, shell=True, capture_output=True, text=True, check=True)
       
        for line in result.stdout.split("\n"):
            if line == "":continue
            infilelds = line.split("{")[1].split("}")[0].split(",")
            for inf in infilelds:
                for field in fieldstosave:
                    if field in inf:
                        summary[field] = int(inf.split(':')[1].strip())
    except subprocess.CalledProcessError as e:
        print(f"Error querying DAS for {dataset}: {e}")
    return summary


if __name__ == "__main__":
    # parse arguments
    args = get_arguments()
    yaml_file       = args.dataset_yml
    central_dataset = args.central_dataset
    dataset_names   = args.dataset_keys
    dataset_path    = []
    if central_dataset :
        print(f"Using central dataset: {central_dataset}")
        dataset_path.append(central_dataset)

    elif yaml_file and dataset_names:
        print(f"Using YAML file: {yaml_file}")
        print(f"Fetching datasets: {dataset_names}")

        # load the YAML file
        with open(args.dataset_yml, 'r') as f:
            datasets = yaml.safe_load(f)

        # check if dataset exist and fetch dataset path
        for dataset_name in args.dataset_keys:
            if (dataset_name == "*") or (dataset_name in datasets['samples']):
                # Fetch all datasets
                for name, info in datasets['samples'].items():
                    dataset_path.append(info['dataset'])
            elif dataset_name not in datasets['samples']:
                print(f"Dataset name '{dataset_name}' not found in the YAML file.")
                sys.exit(1)

    for dataset in dataset_path:
        print(f"\t> {dataset}")
        this_summary = get_info(dataset)
        print(f"\t{this_summary}")

        if this_summary.get("nfiles", -1) > MAXCRABFILES:
            nsplits = this_summary["nfiles"] // MAXCRABFILES + 1
            print(f"WARNING : more than {MAXCRABFILES} files --> splitting by {nsplits}")
