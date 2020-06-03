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


def make_positions_and_route_ids(
        solution: Dict[str, Any],
        instance: Dict[str, Any]
) -> (List[int], List[int]):
    pts = instance["points"]
    nodes = len(pts)

    positions = [-1] * nodes
    route_id = [-1] * nodes
    for r, route in enumerate(solution["routes"]):
        for pos, node in enumerate(route):
            positions[node] = pos
            route_id[node] = r

    return positions, route_id


def visiting_order(point: Dict[str, int]) -> (int, int):
    node = point["id"]
    pickup = point["pickup"]
    delivery = point["delivery"]

    before = pickup
    after = node
    if pickup == 0:
        before = node
        after = delivery

    return before, after


def nodes_are_in_order_in_same_routes(
        solution: Dict[str, Any],
        instance: Dict[str, Any]
):
    pts = instance["points"]
    positions, route_id = make_positions_and_route_ids(solution, instance)

    for pt in pts[1:]:  # skip checking depot
        before, after = visiting_order(pt)

        if route_id[before] != route_id[after]:
            raise Infeasible(
                f"Nodes {before} and {after} are not in the same route: "
                f"{before} is in route {route_id[before] + 1}, and "
                f"{after} is in route {route_id[after] + 1}."
            )

        if positions[before] >= positions[after]:
            raise Infeasible(
                f"Node order violated: "
                f"node {before} should be visited before {after}, "
                f"but in route {route_id[after] + 1} "
                f"node {before} is in position {positions[before]}, and "
                f"{after} is in position {positions[after]}."
            )


def verify_ll(solution: Dict[str, Any], instance: Dict[str, Any]):
    verify_gh(solution, instance)
    nodes_are_in_order_in_same_routes(solution, instance)
