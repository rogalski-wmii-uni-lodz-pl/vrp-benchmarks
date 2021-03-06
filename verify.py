import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Any
from parse_solution import parse_solution
from parse_instance import parse_instance
from feasibility import dist, verify_gh, Infeasible, verify_ll
import decimal


class NoSuchInstance(Exception):
    pass


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
        raise NoSuchInstance(
            f"Instance name {inst} does not match any instance")


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
    if len(inst) >= 11:
        raise Infeasible(f"Instance name too long {len(inst)} >= 10")
    if len(inst) < 5:
        raise Infeasible(f"Instance name too short {len(inst)} < 5")

    check_instance_name(inst)
    for r, route in enumerate(solution["routes"]):
        check_route_nodes(route, r + 1)


def read_instance(location: Path, benchmark: str, instance: str) -> List[str]:
    check_instance_name(instance)
    path = (location / benchmark / (instance + ".txt")).resolve()
    if not os.path.isfile(path):
        raise NoSuchInstance(instance)
    return read_file(path)


def verify(solution: Dict[str, Any], instance: Dict[str, Any]):
    check_sanity(solution)

    if (solution["benchmark"] != "LiLim"):
        verify_gh(solution, instance)
    else:
        verify_ll(solution, instance)


def is_valid(
        solution: Dict[str, Any],
        instance: Dict[str, Any]
) -> (bool, str):
    try:
        verify(solution, instance)
        return True, "OK"
    except Infeasible as infeasibility:
        return False, infeasibility.args[0]


def total_distance(solution: Dict[str, Any], instance: Dict[str, Any]):
    distance = 0

    pts = instance["points"]

    for route in solution["routes"]:
        for a, b in zip(route, route[1:]):
            distance += dist(pts[a], pts[b])

    return distance


def parse_solution_and_read_instance(file_contents):
    solution = parse_solution(file_contents)

    instance_file = read_instance(
        instances_location,
        solution["benchmark"],
        solution["instance"])

    instance = parse_instance(instance_file)
    return solution, instance


def read_solution_and_instance(solution_path):
    file_contents = read_file(solution_path)
    return parse_solution_and_read_instance(file_contents)


def verify_file_contents(file_contents, approximation: int = 4):
    solution, instance = parse_solution_and_read_instance(file_contents)

    ok, err = is_valid(solution, instance)

    status = f"ERROR {err}"
    routes = 0
    distance = 0
    rounded = 0
    status = ""
    feasible = False

    if ok:
        routes = len(solution["routes"])
        distance = total_distance(solution, instance)
        rounded = round(distance, approximation)
        status = f"OK {routes} {rounded}"
        feasible = True

    return {
        "solution": solution,
        "status": status,
        "distance": distance,
        "rounded": rounded,
        "feasible": feasible,
        "errors": err
    }


def verify_file(path, approximation: int = 4):
    contents = read_file(path)
    out = verify_file_contents(contents, approximation)

    print(
        path,
        out["solution"]["benchmark"],
        out["solution"]["instance"],
        out["status"],
    )


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc not in [2, 3]:
        usage()
    elif argc == 2:
        verify_file(sys.argv[1])
    else:
        verify_file(sys.argv[1], int(sys.argv[2]))
