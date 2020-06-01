from typing import List, Dict, Any
from parse_solution import to_numbers


gh_line = [
    "id",
    "x",
    "y",
    "demand",
    "earliest",
    "latest",
    "service",
]

lilim_line = [
    *gh_line,
    "pickup",
    "delivery",
]


def parse_instance(lines: List[str]) -> Dict[str, Any]:
    if lines[0][0] in 'rc':
        return parse_instance_file(lines, gh_line, 4, 9)

    return parse_instance_file(lines, lilim_line, 0, 1)


def parse_instance_file(
        lines: List[str],
        line_spec: List[str],
        vehicle_row: int,
        points_start: int
) -> Dict[str, Any]:

    vehicles, capacity = to_numbers(lines[vehicle_row])[:2]

    points = []

    for line in lines[points_start:]:
        if line:
            splitted = to_numbers(line)
            point = dict(zip(line_spec, splitted))

            points.append(point)

    return {
        "vehicles": vehicles,
        "capacity": capacity,
        "points": points
    }
