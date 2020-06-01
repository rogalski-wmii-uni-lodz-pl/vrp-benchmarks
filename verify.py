import sys
import re
from typing import List, Dict, Any
from parse_solution import parse_solution
from parse_instance import parse_instance
from pathlib import Path
import decimal

decimal.getcontext().prec = 100

script_location = Path(__file__).parent
instances_location = script_location / "instances"


def read_file(path) -> List[str]:
    with open(path) as fd:
        return list(fd)


def usage():
    print(f"{sys.argv[0]} path/to/file)")
    print(" verify a solution in the sintef format:")
    print("""
Instance name : [name]
Authors : [who]
Date: [when]
Reference: [where]
Solution
Route 1: 1 2 3 ...
Route 2: 4 5 6 ...
.
.
.
Route n: ...""")


def check_instance_name(inst: str):
    onehundreds = re.match(r"l(r|c|rc)[12][01][0-9]", inst)
    rest = re.match(r"l?(r|c|rc)[12]_(2|4|6|8|10)_([1-9]|10)", inst)
    if not onehundreds and not rest:
        raise Exception(f"instance name {inst} does not match any instance")


def check_route_nodes(route: List[int], r: int):
    if len(route) < 3:
        raise Exception(f"route {r}: too short (< 3): {route}")

    for i, n in enumerate(route[1:-1]):
        if n == 0:
            raise Exception(
                f"route {r}: "
                f"{i}-th client ({n}) is a depot: "
                f"{route}")
        if n < 0:
            raise Exception(
                f"route {r}: "
                f"{i}-th client ({n}) is negative: "
                f"{route}")


def check_sanity(solution: Dict[str, Any]):
    inst = solution["instance"]
    if len(inst) >= 10:
        raise Exception(f"instance name too long {len(inst)} >= 10")
    if len(inst) < 5:
        raise Exception(f"instance name too short {len(inst)} < 5")

    check_instance_name(inst)
    for r, route in enumerate(solution["routes"]):
        check_route_nodes(route, r + 1)


def read_instance(benchmark: str, instance: str) -> List[str]:
    path = (instances_location / benchmark / (instance + ".txt")).resolve()
    return read_file(path)


def verify():
    path = sys.argv[1]
    file_contents = read_file(path)
    solution = parse_solution(file_contents)

    # print(solution)
    check_sanity(solution)

    instance_file = read_instance(solution["benchmark"], solution["instance"])

    instance = parse_instance(instance_file)

    distance = 0

    pts = instance["points"]

    for route in solution["routes"]:
        for a, b in zip(route, route[1:]):
            distance += dist(pts[a], pts[b])

    print(
        solution["benchmark"],
        solution["instance"],
        len(solution["routes"]),
        distance
    )


def dist(a: Dict[str, int], b: Dict[str, int]) -> decimal.Decimal:
    xs = decimal.Decimal(a["x"] - b["x"])
    ys = decimal.Decimal(a["y"] - b["y"])

    return ((xs * xs) + (ys * ys)).sqrt()


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc != 2:
        usage()
    else:
        verify()
