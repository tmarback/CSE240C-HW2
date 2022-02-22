#!/usr/bin/python3

import re
import pandas as pd
from pathlib import Path
from typing import Mapping, Union

from run_all_traces import RES_DIR

OUT_FILE = Path( 'results.csv' )

RESULT_PATTERN = re.compile( r"""
CPU \d+ cummulative IPC: (?P<ipc>\d+\.\d+) instructions: (?P<instructions>\d+) cycles: (?P<cycles>\d+)\s*
\s*LLC TOTAL\s+ACCESS:\s+(?P<total_access>\d+)\s+HIT:\s+(?P<total_hit>\d+)\s+MISS:\s+(?P<total_miss>\d+)\s*
\s*LLC LOAD\s+ACCESS:\s+(?P<load_access>\d+)\s+HIT:\s+(?P<load_hit>\d+)\s+MISS:\s+(?P<load_miss>\d+)\s*
\s*LLC RFO\s+ACCESS:\s+(?P<rfo_access>\d+)\s+HIT:\s+(?P<rfo_hit>\d+)\s+MISS:\s+(?P<rfo_miss>\d+)\s*
\s*LLC PREFETCH\s+ACCESS:\s+(?P<prefetch_access>\d+)\s+HIT:\s+(?P<prefetch_hit>\d+)\s+MISS:\s+(?P<prefetch_miss>\d+)\s*
\s*LLC WRITEBACK\s+ACCESS:\s+(?P<writeback_access>\d+)\s+HIT:\s+(?P<writeback_hit>\d+)\s+MISS:\s+(?P<writeback_miss>\d+)
""" )

def parse_results( file: Path ) -> Mapping[str, Union[int, float]]:
    
    with open( file, 'r' ) as f:
        data = f.read()

    if not ( results := RESULT_PATTERN.search( data ) ):
        raise Exception( "No results found" )
    
    return { k: float( v ) if k == 'ipc' else int( v ) for k, v in results.groupdict().items() }

def main():

    results = [
        {
            'replacement': replacement.name,
            'config': config.name,
            **parse_results( result_file ),
        } for replacement in RES_DIR.iterdir() for config in replacement.iterdir() for result_file in config.iterdir()
    ]

    pd.DataFrame( results ).to_csv( OUT_FILE )

if __name__ == '__main__':
    main()