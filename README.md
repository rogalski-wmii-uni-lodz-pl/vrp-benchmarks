# vrp-benchmarks
A solution checker for CVRPTW (Gehring-Homberger) and PDP (Li-Lim) solutions in Sintef format, plus a clone of best known solutions from https://www.sintef.no/projectweb/top/, and an automated table generator for them.

# Benchmarks
Last updated: [2023-03-08](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/improvements.md#2023-05-22-1-new)

## [full csv](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.csv)

## [PDPTW](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#li-and-lim-pdptw-benchmark)
- [100 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#100-clients)
- [200 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#200-clients)
- [400 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#400-clients)
- [600 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#600-clients)
- [800 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#800-clients)
- [1000 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#1000-clients)

## [CVRPTW](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#gehring-homberger-cvrptw-benchmark)
- [200 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#200-clients-1)
- [400 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#400-clients-1)
- [600 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#600-clients-1)
- [800 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#800-clients-1)
- [1000 clients](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/tables.md#1000-clients-1)

## [improvements csv](https://github.com/rogalski-wmii-uni-lodz-pl/vrp-benchmarks/blob/master/improvements.csv)

## Checker
Run `python3 verify.py sol [precision=4]` to verify one solution sol in the sintef format, with result rounded to optional precision (default 4).

## Generating tables
First, add files using `python3 adder file1 file2...`, which should create a directory with todays date in the best_known_solutions directory.
Afterwards, run `python bests.py` to generate `tables.md` and `tables.csv`.

## Generating improvements
`python3 improvements.py`


Contributions welcome
