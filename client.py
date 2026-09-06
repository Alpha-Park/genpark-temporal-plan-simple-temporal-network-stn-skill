"""
Temporal Plan Simple Temporal Network STN Skill Client
Pure Python Standard Library implementation of Simple Temporal Networks (STN) (Dechter et al.).
Evaluates temporal constraints (X_j - X_i in [a, b]), checks consistency via Floyd-Warshall,
and computes earliest/latest start time bounds for agent tasks.
"""

from typing import List, Dict, Any, Tuple, Optional, Set


class SimpleTemporalNetwork:
    """
    STN distance graph solver.
    Nodes represent time points (e.g. task start/finish).
    Constraint X_j - X_i in [a_ij, b_ij] is mapped to directed edges:
    - edge(i -> j) with weight b_ij  (X_j - X_i <= b_ij)
    - edge(j -> i) with weight -a_ij (X_i - X_j <= -a_ij <=> X_j - X_i >= a_ij)
    """

    def __init__(self):
        self.timepoints: Set[str] = {"origin"}
        self.constraints: List[Dict[str, Any]] = []

    def add_timepoint(self, name: str):
        """Add timepoint to network."""
        self.timepoints.add(name.strip())

    def add_constraint(self, source: str, target: str, min_duration: float, max_duration: float):
        """
        Constrain duration between source and target: target - source in [min_duration, max_duration]
        """
        self.timepoints.add(source)
        self.timepoints.add(target)
        self.constraints.append({
            "source": source,
            "target": target,
            "min_duration": float(min_duration),
            "max_duration": float(max_duration)
        })

    def solve(self) -> Dict[str, Any]:
        """
        Solve STN distance graph using Floyd-Warshall all-pairs shortest paths.
        Detects negative cycles (inconsistency) and calculates earliest/latest schedules.
        """
        nodes = sorted(list(self.timepoints))
        n = len(nodes)
        node_idx = {name: i for i, name in enumerate(nodes)}

        # Initialize distance matrix
        inf = float("inf")
        dist = [[inf] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0.0

        # Build distance graph edges
        for c in self.constraints:
            u = node_idx[c["source"]]
            v = node_idx[c["target"]]
            b_ij = c["max_duration"]
            a_ij = c["min_duration"]

            # Edge u -> v: weight b_ij
            dist[u][v] = min(dist[u][v], b_ij)
            # Edge v -> u: weight -a_ij
            dist[v][u] = min(dist[v][u], -a_ij)

        # Floyd-Warshall
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] != inf and dist[k][j] != inf:
                        if dist[i][k] + dist[k][j] < dist[i][j]:
                            dist[i][j] = dist[i][k] + dist[k][j]

        # Check negative cycles (inconsistency)
        is_consistent = True
        for i in range(n):
            if dist[i][i] < 0:
                is_consistent = False
                break

        if not is_consistent:
            return {
                "is_consistent": False,
                "schedule": None,
                "error": "Temporal constraints are inconsistent (negative cycle detected)."
            }

        # Calculate Earliest and Latest times relative to 'origin'
        origin_idx = node_idx["origin"]
        schedule = {}
        for name in nodes:
            idx = node_idx[name]
            # Earliest: -dist[idx][origin] (lower bound)
            # Latest: dist[origin][idx] (upper bound)
            earliest = -dist[idx][origin_idx] if dist[idx][origin_idx] != inf else 0.0
            latest = dist[origin_idx][idx] if dist[origin_idx][idx] != inf else float("inf")
            schedule[name] = {
                "earliest_time": earliest,
                "latest_time": latest,
                "slack": latest - earliest if latest != inf and earliest != inf else float("inf")
            }

        return {
            "is_consistent": True,
            "schedule": schedule,
            "node_count": n
        }
