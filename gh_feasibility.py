from typing import List, Dict, Any
import itertools
import decimal

decimal.getcontext().prec = 128


class Infeasible(Exception):
    pass


def has_all_nodes(solution: Dict[str, Any], instance: Dict[str, Any]):
    nodes = set(node for route in solution["routes"] for node in route)

    nodes_in_instance = len(instance["points"])

    if len(nodes) < nodes_in_instance:
        missing = set(range(nodes_in_instance)) - nodes
        raise Infeasible(f"Not all nodes served: {missing}")
    elif len(nodes) > nodes_in_instance:
        additional = nodes - set(range(nodes_in_instance))
        raise Infeasible(f"Additional nodes served: {additional}")


def not_too_many_routes(solution: Dict[str, Any], instance: Dict[str, Any]):
    routes = len(solution["routes"])
    vehicles = instance["vehicles"]
    if routes > vehicles:
        raise Infeasible(f"Too many vehicles: {routes} > {vehicles}")


def capacity_is_within_limits(
        route: List[int],
        r: int,
        instance: Dict[str, Any]
):
    capacity = instance["capacity"]
    pts = instance["points"]

    demands = [
        pts[node]["demand"]
        for node in route
    ]

    accumulations = list(itertools.accumulate(demands))

    for i, acc in enumerate(accumulations):
        if acc > capacity:
            raise Infeasible(
                f"Route {r} exceeds max capacity ({acc} > {capacity}) "
                f"at {route[i]} (on position {i}): "
                f"{route}, accumulations {accumulations}"
            )
        if acc < 0:
            raise Infeasible(
                f"Route {r} has negative load ({acc} < 0) "
                f"at {route[i]} (on position {i}): "
                f"{route}, accumulations {accumulations}"
            )


def dist(src: Dict[str, int], dst: Dict[str, int]) -> decimal.Decimal:
    xs = decimal.Decimal(src["x"] - dst["x"])
    ys = decimal.Decimal(src["y"] - dst["y"])

    return ((xs * xs) + (ys * ys)).sqrt()


def never_too_late(
        route: List[int],
        r: int,
        instance: Dict[str, Any]
):
    pts = instance["points"]
    time = decimal.Decimal(pts[0]["earliest"])
    for i, edge in enumerate(zip(route, route[1:])):
        src, dst = [pts[x] for x in edge]
        departure = time + src["service"]
        travel = dist(src, dst)
        arrival = departure + travel
        earliest_service = max(arrival, dst["earliest"])
        if earliest_service > dst["latest"]:
            raise Infeasible(
                f"In route {r}: arrived too late "
                f'({round(earliest_service, 16)} > {dst["latest"]}) '
                f'at {dst["id"]} (on position {i}): {route}'
            )

        time = earliest_service


def verify_gh(solution: Dict[str, Any], instance: Dict[str, Any]):
    has_all_nodes(solution, instance)
    not_too_many_routes(solution, instance)
    for r, route in enumerate(solution["routes"]):
        never_too_late(route, r + 1, instance)
        capacity_is_within_limits(route, r + 1, instance)
