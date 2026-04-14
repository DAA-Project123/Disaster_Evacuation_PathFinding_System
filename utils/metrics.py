from __future__ import annotations


def safe_div(numerator: float, denominator: float, default: float = 0.0) -> float:
    if denominator == 0:
        return default
    return float(numerator) / float(denominator)


def pct_change(current: float, previous: float) -> float | None:
    if previous == 0:
        return None
    return (current - previous) / previous * 100.0


def summarize_algo_row(row: dict) -> dict:
    """Normalize algorithm comparison row keys for API consumers."""
    return {
        "algorithm": row.get("Algorithm", ""),
        "path_found": bool(row.get("Path Found", False)),
        "path_length": int(row.get("Path Length", 0)),
        "nodes_explored": int(row.get("Nodes Explored", 0)),
        "time_ms": float(row.get("Time (ms)", 0.0)),
        "safety_score": float(row.get("Safety Score", 0.0)),
        "used_air_edges": bool(row.get("used_air_edges", False)),
        "composite_score": float(row.get("Composite Score", 0.0)),
    }
