import os
import json
import csv
import platform
from typing import List, Dict, Any
from copy import deepcopy
from pathlib import Path
from collections import defaultdict
from parse_solution import Reference, parse_solution


script_location = Path(__file__).parent
bks_location = script_location / "best_known_solutions"
unknown = "???"


def read_overwrites():
    with open(script_location / "overwrite.json") as fd:
        over = [x for x in json.load(fd) if x]
        overwrites = dict(
            (o["file"], o["who"])
            for o in over
        )
    return overwrites


def read_refs():
    references = {unknown: unknown}
    with open(script_location / "refs.json") as fd:
        refs = json.load(fd)
        for reference in refs:
            for variant in refs[reference]:
                ref = Reference(variant["authors"], variant["reference"])
                references[ref] = reference

    return references


def read_file(path) -> List[str]:
    with open(path) as fd:
        return list(fd)


def get_reference(lines: List[str]) -> Reference:
    if len(lines) != 0:
        return parse_solution(lines)["who"]

    return unknown


def overwrite(
        filename: str,
        overwrites: Dict[str, Any],
        who_detail
) -> (str, List[str]):

    if filename in overwrites:
        who = overwrites[filename]
        if who_detail == unknown or (who_detail[0] in who):
            who_detail = who
    else:
        who = who_detail

    return who, who_detail


def parse_filename(filename: str) -> (str, str, str):
    inst, res = filename.split(".", 1)
    routes, dist_dot_txt = res.split('_')
    dist = dist_dot_txt.rsplit('.', 1)[0]

    _, fraction = dist.split(".")

    dist += "0" * (4 - len(fraction))

    return inst, routes, dist


def is_better(previous_best, routes, distance):
    previous_best_rs = int(previous_best["routes"])
    rs = int(routes)

    better_routes = (rs < previous_best_rs)
    same_routes = (rs == previous_best_rs)

    better_dist = (float(distance) < float(previous_best["distance"]))

    return better_routes or (same_routes and better_dist)


def generate_bks(
        refs,
        overwrites,
        inst_path):
    db = defaultdict(list)
    dates = (os.listdir(inst_path))
    for date in sorted(dates):
        path = inst_path / date
        for filename in os.listdir(path):
            full_path = path / filename
            solution_file = read_file(full_path)

            inst, routes, dist = parse_filename(filename)

            reference = get_reference(solution_file)

            who_detail = [refs[reference]]
            who, who_detail = overwrite(filename, overwrites, who_detail)

            if inst not in db or is_better(db[inst][-1], routes, dist):
                db[inst].append({
                    "instance": inst,
                    "when": date,
                    "routes": routes,
                    "distance": dist,
                    "who": " & ".join(sorted(who)),
                    "detailed": " & ".join(sorted(who_detail)),
                    "url": full_path
                })

    return db


def make_table(
        db: Dict[str, List[Any]], insts: List[str]) -> List[Dict[str, Any]]:
    out = []

    for inst in insts:
        best = db[inst][-1]
        out.append(best)
    return out


left = ":---"
right = "---:"
center = ":---:"


def mdrow(row: List[str]) -> str:
    return " | ".join(str(r) for r in row)


def make_md_table(table) -> List[str]:
    tbl = deepcopy(table)
    out = []
    keys = ["instance", "routes", "distance", "when", "who", "notes"]
    align = [center, center, center, center, center, center]
    out.append(mdrow(keys))
    out.append(mdrow(align))

    for row in tbl:
        row["distance"] = f'[{row["distance"]}]({row["url"]})'

        row["notes"] = ""
        if row["who"] != row["detailed"]:
            row["notes"] = f'contributed by {row["detailed"]}'

        fields = [row[what] for what in keys]

        out.append(mdrow(fields))

    return out


def make_full_bks_db():
    refs = read_refs()
    overwrites = read_overwrites()
    db = {}
    for benchmark in ["LiLim", "GehringHomberger"]:
        db = {**db, **generate_bks(refs, overwrites, bks_location / benchmark)}

    return db


def make_benchmarks():
    with open(script_location / "tables.json") as fd:
        tables = json.load(fd)

    names = {
        "LiLim": "Li and Lim PDPTW Benchmark",
        "GehringHomberger": "Gehring-Homberger CVRPTW Benchmark"
    }

    refs = read_refs()
    overwrites = read_overwrites()
    firstline = True
    with open("tables.md", 'w') as out, open("tables.csv", 'w') as csv_out:
        if platform.system() == "Linux":
            c = csv.writer(csv_out, lineterminator='\n')
        else:
            c = csv.writer(csv_out)

        for benchmark in tables:
            db = generate_bks(refs, overwrites, bks_location / benchmark)

            out.write(f"# {names[benchmark]}\n")
            for size in tables[benchmark]:
                groups = tables[benchmark][size]
                out.write(f"## {size} clients\n")

                for instances in groups:
                    table = make_table(db, instances)
                    mdtable = make_md_table(table)

                    if firstline:
                        c.writerow(["benchmark", "clients", *table[0]])
                        firstline = False

                    for row in table:
                        c.writerow([benchmark, size, *row.values()])

                    for line in mdtable:
                        out.write(line + "\n")

                    out.write("\n")


if __name__ == "__main__":
    make_benchmarks()
