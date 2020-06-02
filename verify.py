import sys
import re
from typing import List, Dict, Any
from parse_solution import parse_solution
from parse_instance import parse_instance
from pathlib import Path
from gh_feasibility import dist, verify_gh, Infeasible
import decimal

decimal.getcontext().prec = 128

script_location = Path(__file__).parent
instances_location = script_location / "instances"


def read_file(path) -> List[str]:
    with open(path) as fd:
        return list(fd)


def usage():
    print(f"{sys.argv[0]} path/to/file [apr=4]")
    print(
        " verify, calculate the distance and approximate it to apr digits "
        "(default 4) of a solution in the sintef format,")
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
        raise Infeasible(f"Instance name {inst} does not match any instance")


def check_route_nodes(route: List[int], r: int):
    if len(route) < 3:
        raise Infeasible(f"Route {r}: too short (< 3): {route}")

    for i, n in enumerate(route[1:-1]):
        if n == 0:
            raise Infeasible(
                f"Route {r}: {i}-th client ({n}) is a depot: {route}"
            )
        if n < 0:
            raise Infeasible(
                f"Route {r}: {i}-th client ({n}) is negative: {route}"
            )


def check_sanity(solution: Dict[str, Any]):
    inst = solution["instance"]
    if len(inst) >= 10:
        raise Infeasible(f"Instance name too long {len(inst)} >= 10")
    if len(inst) < 5:
        raise Infeasible(f"Instance name too short {len(inst)} < 5")

    check_instance_name(inst)
    for r, route in enumerate(solution["routes"]):
        check_route_nodes(route, r + 1)


def read_instance(benchmark: str, instance: str) -> List[str]:
    path = (instances_location / benchmark / (instance + ".txt")).resolve()
    return read_file(path)


def verify(solution: Dict[str, Any], instance: Dict[str, Any]):
    check_sanity(solution)

    if (solution["benchmark"] != "LiLim"):
        verify_gh(solution, instance)
    else:
        verify_gh(solution, instance)


def total_distance(solution: Dict[str, Any], instance: Dict[str, Any]):
    distance = 0

    pts = instance["points"]

    for route in solution["routes"]:
        for a, b in zip(route, route[1:]):
            distance += dist(pts[a], pts[b])

    return distance


def verify_file(approximation: int = 4):
    path = sys.argv[1]
    file_contents = read_file(path)
    solution = parse_solution(file_contents)

    # print(solution)

    instance_file = read_instance(solution["benchmark"], solution["instance"])

    instance = parse_instance(instance_file)

    try:
        verify(solution, instance)

        print(
            path,
            solution["benchmark"],
            solution["instance"],
            len(solution["routes"]),
            round(total_distance(solution, instance), approximation)
        )
    except Infeasible as infeasibility:
        print(
            path,
            solution["benchmark"],
            solution["instance"],
            "ERROR:",
            infeasibility.args[0]
        )


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc not in [2, 3]:
        usage()
    elif argc == 2:
        verify_file()
    else:
        verify_file(int(sys.argv[2]))
