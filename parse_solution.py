from typing import List, Dict, Any
from collections import namedtuple

Reference = namedtuple('ref', 'author reference')


def after_colon(s: str) -> str:
    return s.split(':', 1)[1].strip()


def to_numbers(line: str) -> List[int]:
    return [
        int(x)
        for x in line.split()
        if x
    ]


def add_depots(route: List[int], depot=0) -> List[int]:
    return [depot, *route, depot]


def parse_route(line: str) -> List[int]:
    route = after_colon(line)
    parsed = to_numbers(route)
    return add_depots(parsed)


def instance_name_to_benchmark(instance: str):
    if instance[0] == "l":
        return "LiLim"

    return "GehringHomberger"


def parse_solution(lines: List[str]) -> Dict[str, Any]:
    instance = after_colon(lines[0]).lower()

    authors = after_colon(lines[1])
    reference = after_colon(lines[3])

    # line number of the first route
    routes_start = 5

    routes = [
        parse_route(line)
        for line in lines[routes_start:]
        if line.strip()
    ]

    return {
        "benchmark": instance_name_to_benchmark(instance),
        "instance": instance,
        "routes": routes,
        "who": Reference(authors, reference)
    }
