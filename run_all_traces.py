#!/usr/bin/python3

import argparse
import multiprocessing
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from tqdm import tqdm

TRACE_DIR = Path( './traces_gz' )
SRC_DIR = Path( './replacements' )
SRC_DONE_DIR = Path( './replacements_done' )
BIN_DIR = Path( './bin' )
OUT_DIR = Path( './output' )
RES_DIR = Path( './results' )

PARALLEL_JOBS = multiprocessing.cpu_count()

DEFAULT_N_WARM = 10
DEFAULT_N_SIM = 100

# n_warm and n_sim should be in millions of instructions
def run_traces( replacement: str, config: str, n_warm: int = DEFAULT_N_WARM, n_sim: int = DEFAULT_N_SIM, move_src: bool = False, move_out = False ) -> None:

    BIN_DIR.mkdir( parents = True, exist_ok = True )

    log_dir = OUT_DIR / replacement / config
    log_dir.mkdir( parents = True, exist_ok = True )

    source = SRC_DIR / f'{replacement}.cc'
    executable = BIN_DIR / f'{replacement}-{config}'

    n_warm *= 10 ** 6
    n_sim *= 10 ** 6

    tqdm.write( f"Running with {PARALLEL_JOBS} parallel jobs" )

    subprocess.check_call( [ 'g++', '-Wall', '--std=c++11', '-o', executable, source, f'lib/{config}.a' ] )

    tracefiles = list( TRACE_DIR.iterdir() )

    progress_lock = Lock()
    with tqdm( total = len( tracefiles ), desc = f"Running traces on {replacement} w/ {config}", leave = None ) as progress:
            
        def run_trace( trace: str ):

            try:
                tqdm.write( f"=====[ STARTING TRACE: {trace} ]=====" )
                with open( log_dir / f'{trace}.txt', 'w' ) as log:
                    subprocess.check_call( [ executable, '-warmup_instructions', str( n_warm ), '-simulation_instructions', str( n_sim ), 
                            '-traces', TRACE_DIR / trace ], stdout = log, stderr = subprocess.STDOUT )
                tqdm.write( f"=====[ FINISHED TRACE: {trace} ]=====" )
                with progress_lock:
                    progress.update()
            except subprocess.CalledProcessError as e:
                tqdm.write( f"Error while executing simuation:\n\t{e.stdout}\n\t{e.stderr}" )
            except Exception as e:
                tqdm.write( f"Error in executor: {e}" )

        with ThreadPoolExecutor( max_workers = PARALLEL_JOBS ) as executor:

            for trace in tracefiles:
                executor.submit( run_trace, trace.name )

    if move_src:
        SRC_DONE_DIR.mkdir( parents = True, exist_ok = True )
        source.rename( SRC_DONE_DIR / f'{replacement}.cc' )
    if move_out:
        res_dir = RES_DIR / replacement / config
        res_dir.mkdir( parents = True, exist_ok = True )
        log_dir.rename( res_dir )

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument( 'replacement' )
    parser.add_argument( 'config' )
    parser.add_argument( '--warm', type = int, default = DEFAULT_N_WARM, help = "In millions of instructions" )
    parser.add_argument( '--sim', type = int, default = DEFAULT_N_SIM, help = "In millions of instructions" )

    args = parser.parse_args()

    run_traces( args.replacement, args.config, args.warm, args.sim )
