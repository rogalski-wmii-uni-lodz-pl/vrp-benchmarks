import os
import json
from typing import List, Dict, Any
from pathlib import Path
from collections import defaultdict
from parse_solution import Reference, parse_solution


script_location = Path(__file__).parent
bks_location = script_location / "best_known_solutions"
unknown = "???"


def read_overwrites():
    with open("overwrite.json") as fd:
        over = [x for x in json.load(fd) if x]
        overwrites = dict(
            (o["file"], o["who"])
            for o in over
        )
    return overwrites


def read_refs():
    references = {unknown: unknown}
    with open("refs.json") as fd:
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

    dist += "0"*(4 - len(fraction))

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

            if who == who_detail:
                who_detail = ""

            if not db[inst] or is_better(db[inst][-1], routes, dist):
                db[inst].append({
                    "instance": inst,
                    "when": date,
                    "routes": routes,
                    "distance": dist,
                    "who": " & ".join(who),
                    "detailed": " & ".join(sorted(who_detail)),
                    "url": full_path
                })

    return db


left = ":---"
right = "---:"
center = ":---:"


def mdrow(row: List[str]) -> str:
    return " | ".join(str(r) for r in row)


def make_md_table(benchmark: str, groups: List[str]) -> str:
    out = []
    keys = ["instance", "when", "who", "routes", "distance", "url", "detailed"]
    align = [center, center, center, center, center, center, center]
    refs = read_refs()
    overwrites = read_overwrites()
    db = generate_bks(refs, overwrites, bks_location / benchmark)

    for insts in groups:
        out.append(mdrow(keys))
        out.append(mdrow(align))

        for inst in insts:
            best = db[inst][-1]

            for what in ["instance", "routes", "distance"]:
                best[what] = f"`{best[what]}`"

            best["url"] = f'[download]({best["url"]})'

            row = [best[what] for what in keys]

            out.append(mdrow(row))

        out.append("")

    return out


def make_benchmarks():
    with open("./tables.json") as fd:
        tables = json.load(fd)

    names = {
        "LiLim": "Li and Lim PDPTW Benchmark",
        "GehringHomberger": "Gehring-Homberger CVRPTW Benchmark"
    }

    for benchmark in tables:
        print(f"# {names[benchmark]}")
        for size in tables[benchmark]:
            instances = tables[benchmark][size]
            mdtable = make_md_table(benchmark, instances)

            print(f"## {size} clients")

            for line in mdtable:
                print(line)


if __name__ == "__main__":
    make_benchmarks()
