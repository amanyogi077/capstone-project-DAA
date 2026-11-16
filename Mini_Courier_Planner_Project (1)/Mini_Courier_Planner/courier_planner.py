"""
Mini-Courier Planner
Course: Design & Analysis of Algorithms (ETCCDA302)

Algorithms:
1. Merge Sort: orders parcels by priority and deadline.
2. 0/1 Knapsack (Dynamic Programming): selects the highest-value set of parcels
   that fits in the courier's weight capacity.
3. Dijkstra: calculates shortest paths in a non-negative weighted graph.
4. Nearest Neighbor: builds an approximate multi-stop delivery tour using
   shortest-path distances between delivery locations.

Run:
    python courier_planner.py
    python courier_planner.py --capacity 10
    python courier_planner.py --parcels data/parcels.csv --edges data/roads.csv
"""

from __future__ import annotations
import argparse
import csv
import heapq
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional

PRIORITY_SCORE = {"High": 100, "Medium": 60, "Low": 30}
PRIORITY_RANK = {"High": 0, "Medium": 1, "Low": 2}


@dataclass(frozen=True)
class Parcel:
    parcel_id: str
    destination: str
    weight: float
    priority: str
    deadline: str
    value: int


def merge_sort_parcels(parcels: List[Parcel]) -> List[Parcel]:
    """Stable merge sort: priority first, then earlier deadline."""
    if len(parcels) <= 1:
        return parcels[:]
    mid = len(parcels) // 2
    left = merge_sort_parcels(parcels[:mid])
    right = merge_sort_parcels(parcels[mid:])

    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        key_left = (PRIORITY_RANK[left[i].priority], left[i].deadline, left[i].parcel_id)
        key_right = (PRIORITY_RANK[right[j].priority], right[j].deadline, right[j].parcel_id)
        if key_left <= key_right:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def knapsack_01(parcels: List[Parcel], capacity: float) -> Tuple[List[Parcel], int, float]:
    """
    0/1 Knapsack DP.
    Weights are converted to integer tenths of kg to support decimal weights.
    Returns selected parcels, maximum value, and used weight.
    """
    if capacity < 0:
        raise ValueError("Capacity cannot be negative.")
    scale = 10
    cap = int(round(capacity * scale))
    weights = [int(round(p.weight * scale)) for p in parcels]
    n = len(parcels)
    dp = [[0] * (cap + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt = weights[i - 1]
        val = parcels[i - 1].value
        for c in range(cap + 1):
            dp[i][c] = dp[i - 1][c]
            if wt <= c:
                dp[i][c] = max(dp[i][c], val + dp[i - 1][c - wt])

    selected = []
    c = cap
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            selected.append(parcels[i - 1])
            c -= weights[i - 1]
    selected.reverse()
    used = sum(p.weight for p in selected)
    return selected, dp[n][cap], used


def load_parcels(path: Path) -> List[Parcel]:
    parcels = []
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            priority = row["priority"].strip().title()
            if priority not in PRIORITY_SCORE:
                raise ValueError(f"Invalid priority for {row['parcel_id']}: {priority}")
            weight = float(row["weight"])
            if weight <= 0:
                raise ValueError(f"Weight must be positive for {row['parcel_id']}")
            parcels.append(Parcel(
                parcel_id=row["parcel_id"].strip(),
                destination=row["destination"].strip(),
                weight=weight,
                priority=priority,
                deadline=row["deadline"].strip(),
                value=int(row.get("value") or PRIORITY_SCORE[priority])
            ))
    return parcels


def load_graph(path: Path) -> Dict[str, List[Tuple[str, float]]]:
    graph: Dict[str, List[Tuple[str, float]]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            a, b, distance = row["from"].strip(), row["to"].strip(), float(row["distance"])
            if distance < 0:
                raise ValueError("Dijkstra requires non-negative road distances.")
            graph.setdefault(a, []).append((b, distance))
            graph.setdefault(b, []).append((a, distance))
    return graph


def dijkstra(graph: Dict[str, List[Tuple[str, float]]], source: str):
    """Return shortest distances and predecessor map from source."""
    distances = {node: math.inf for node in graph}
    previous: Dict[str, Optional[str]] = {node: None for node in graph}
    if source not in graph:
        raise ValueError(f"Location '{source}' is not present in the road graph.")
    distances[source] = 0.0
    pq = [(0.0, source)]

    while pq:
        current_dist, node = heapq.heappop(pq)
        if current_dist > distances[node]:
            continue
        for neighbor, edge_weight in graph[node]:
            new_dist = current_dist + edge_weight
            if new_dist < distances.get(neighbor, math.inf):
                distances[neighbor] = new_dist
                previous[neighbor] = node
                heapq.heappush(pq, (new_dist, neighbor))
    return distances, previous


def reconstruct_path(previous: Dict[str, Optional[str]], source: str, target: str) -> List[str]:
    if source == target:
        return [source]
    if target not in previous:
        return []
    path = []
    node: Optional[str] = target
    while node is not None:
        path.append(node)
        node = previous.get(node)
    path.reverse()
    return path if path and path[0] == source else []


def all_pairs_shortest_paths(graph: Dict[str, List[Tuple[str, float]]]):
    distances = {}
    paths = {}
    for source in graph:
        dist, prev = dijkstra(graph, source)
        distances[source] = dist
        paths[source] = {target: reconstruct_path(prev, source, target) for target in graph}
    return distances, paths


def nearest_neighbor_tour(depot: str, destinations: List[str],
                          distances: Dict[str, Dict[str, float]]):
    """Approximate a round trip: depot -> all stops -> depot."""
    stops = list(dict.fromkeys(d for d in destinations if d != depot))
    route = [depot]
    current = depot
    total = 0.0

    while stops:
        reachable = [(distances[current].get(stop, math.inf), stop) for stop in stops]
        leg_distance, next_stop = min(reachable)
        if math.isinf(leg_distance):
            raise ValueError(f"No road path from {current} to any remaining delivery point.")
        total += leg_distance
        route.append(next_stop)
        stops.remove(next_stop)
        current = next_stop

    return_distance = distances[current].get(depot, math.inf)
    if math.isinf(return_distance):
        raise ValueError(f"No return path from {current} to depot {depot}.")
    total += return_distance
    route.append(depot)
    return route, total


def print_table(title: str, headers: List[str], rows: List[List[str]]) -> None:
    print("\n" + title)
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(str(cell)))
    fmt = " | ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(fmt.format(*[str(x) for x in row]))


def run_planner(parcels_path: Path, roads_path: Path, depot: str, capacity: float):
    parcels = load_parcels(parcels_path)
    graph = load_graph(roads_path)

    print("=" * 66)
    print("                 MINI-COURIER PLANNER")
    print("=" * 66)
    print(f"Warehouse: {depot} | Box capacity: {capacity:.1f} kg")
    print(f"Total parcels received: {len(parcels)}")

    sorted_parcels = merge_sort_parcels(parcels)
    print_table(
        "1) PRIORITIZED PARCELS (Merge Sort)",
        ["ID", "Destination", "Weight", "Priority", "Deadline", "Value"],
        [[p.parcel_id, p.destination, f"{p.weight:.1f}", p.priority, p.deadline, str(p.value)]
         for p in sorted_parcels]
    )

    selected, total_value, used_weight = knapsack_01(sorted_parcels, capacity)
    print_table(
        "2) SELECTED PARCELS (0/1 Knapsack DP)",
        ["ID", "Destination", "Weight", "Priority", "Value"],
        [[p.parcel_id, p.destination, f"{p.weight:.1f}", p.priority, str(p.value)]
         for p in selected]
    )
    print(f"Selected value: {total_value} | Used capacity: {used_weight:.1f}/{capacity:.1f} kg")

    distances, paths = all_pairs_shortest_paths(graph)
    destinations = [p.destination for p in selected]
    # Confirm every selected delivery point exists and is reachable from depot.
    for destination in destinations:
        if destination not in graph or math.isinf(distances[depot].get(destination, math.inf)):
            raise ValueError(f"Destination '{destination}' is missing or unreachable from depot '{depot}'.")

    unique_destinations = list(dict.fromkeys(destinations))
    route, route_length = nearest_neighbor_tour(depot, unique_destinations, distances)
    print("\n3) SHORTEST PATHS (Dijkstra)")
    for destination in unique_destinations:
        path = paths[depot][destination]
        distance = distances[depot][destination]
        print(f"{depot} -> {destination}: {' -> '.join(path)} | {distance:.1f} km")

    print("\n4) APPROXIMATE DELIVERY TOUR (Nearest Neighbor)")
    print(" -> ".join(route))
    print(f"Total route length (including return to warehouse): {route_length:.1f} km")

    print("\nSUMMARY")
    print(f"Parcels selected: {len(selected)} of {len(parcels)}")
    print(f"Packing utilization: {(used_weight / capacity * 100 if capacity else 0):.1f}%")
    print(f"Total priority value: {total_value}")
    print(f"Approximate tour distance: {route_length:.1f} km")
    return selected, route, route_length


def main():
    parser = argparse.ArgumentParser(description="Plan courier parcel selection and delivery route.")
    parser.add_argument("--capacity", type=float, default=10.0, help="Courier box capacity in kg (default: 10)")
    parser.add_argument("--depot", default="Warehouse", help="Starting/ending warehouse node")
    parser.add_argument("--parcels", type=Path, default=Path("data/parcels.csv"))
    parser.add_argument("--edges", type=Path, default=Path("data/roads.csv"))
    args = parser.parse_args()
    run_planner(args.parcels, args.edges, args.depot, args.capacity)


if __name__ == "__main__":
    main()
