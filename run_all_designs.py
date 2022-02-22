#!/usr/bin/python3

from pathlib import Path
from tqdm import tqdm

from run_all_traces import run_traces

SRC_DIR = Path( './replacements' )
CONFIGS = ( 'config1', 'config2' )

def main():

    replacements = [ f.stem for f in SRC_DIR.iterdir() ]

    for replacement in tqdm( replacements, desc = "Running each replacement policy", leave = None ):
        for i, config in enumerate( tqdm( CONFIGS, desc = f"Running each config on {replacement}", leave = None ) ):
            run_traces( replacement, config, move_src = ( i == len( CONFIGS ) - 1 ), move_out = True )

if __name__ == '__main__':
    main()