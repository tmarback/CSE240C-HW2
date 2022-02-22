# CSE 240C HW2

Code used to reproduce the results of CRC2 winners and explore the design space.

Running all tests is done by placing the `gz` trace files in `traces_gz/`, the replacement policies to be tested in `replacements/` then running the following script:

```
./run_all_designs.py
```

Completed policies are automatically moved to `replacements_done/` so re-running the script will only run for policies that were not completely evaluated previously.

The resulting logs are placed into `results/`, and can be parsed into a summary CSV (`results.csv`) with the following script:

```
./parse_results.py
```

Note that, for these scripts to work, `python3` must be version 3.8 or higher, and `tqdm` must be installed. For the results script, `pandas` must also be installed.