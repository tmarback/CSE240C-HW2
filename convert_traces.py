#!/usr/bin/python3

import argparse
import multiprocessing
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Lock
from tqdm import tqdm

src = Path( "./traces" )
dst = Path( "./traces_gz" )
done = Path( "./traces_done" )

dst.mkdir( parents = True, exist_ok = True )
done.mkdir( parents = True, exist_ok = True )

PARALLEL_JOBS = multiprocessing.cpu_count()
tqdm.write( f"Running with {PARALLEL_JOBS} parallel jobs" )

tracefiles = list( src.iterdir() )

progress_lock = Lock()
with tqdm( total = len( tracefiles ) ) as progress:
        
    def run_trace( trace: Path ):

        trace_xz = src / f'{trace}.xz'
        trace_gz = dst / f'{trace}.gz'

        tqdm.write( f"=====[ STARTING TRACE: {trace} ]=====")
        try:
            subprocess.check_call( f'xz -d --stdout "{trace_xz}" | gzip > "{trace_gz}"', shell = True )
            trace_xz.rename( done / f'{trace}.xz' )
        except subprocess.CalledProcessError as e:
            tqdm.write( f"Error for trace {trace}:\n\t{e.output}\n\t{e.stderr}" )
            trace_gz.unlink( missing_ok = True )
        except Exception as e:
            tqdm.write( f"Exception: {e}" )
            
        tqdm.write( f"=====[ FINISHED TRACE: {trace} ]=====" )
        with progress_lock:
            progress.update()

    with ThreadPoolExecutor( max_workers = PARALLEL_JOBS ) as executor:

        for trace in tracefiles:
            executor.submit( run_trace, trace.stem ) 
        
tqdm.write( "Finished all traces." )
    
