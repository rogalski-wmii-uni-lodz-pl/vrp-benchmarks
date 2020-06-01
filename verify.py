import sys
import re
from typing import List, Dict, Any


def after_colon(s: str) -> str:
    return s.split(':')[1].strip()


def to_numbers(line: str) -> List[int]:
    return [
        int(x)
        for x in line.split(' ')
        if x
    ]


def add_depots(route: List[int], depot=0) -> List[int]:
    return [depot, *route, depot]


def parse_route(line: str) -> List[int]:
    route = after_colon(line)
    parsed = to_numbers(route)
    return add_depots(parsed)


def instance_name_to_benchmark(instance: str):
    if instance[0] == "L":
        return "LiLim"

    return "GehringHomberger"


def parse_solution(lines: List[str]) -> Dict[str, Any]:
    instance = after_colon(lines[0]).upper()

    # first route line number
    routes_start = 5

    routes = [
        parse_route(line)
        for line in lines[routes_start:]
        if line
    ]

    return {
        "benchmark": instance_name_to_benchmark(instance),
        "instance": instance,
        "routes": routes
    }


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
    onehundreds = re.match(r"L(R|C|RC)[12][01][0-9]", inst)
    rest = re.match(r"L?(R|C|RC)[12]_(2|4|6|8|10)_([1-9]|10)", inst)
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


def verify():
    path = sys.argv[1]
    file_contents = read_file(path)
    solution = parse_solution(file_contents)

    print(
        solution["benchmark"],
        solution["instance"])
    # print(solution)
    check_sanity(solution)


if __name__ == "__main__":
    argc = len(sys.argv)
    if argc != 2:
        usage()
    else:
        verify()
