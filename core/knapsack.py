"""Knapsack optimization with priority queue for rescue planning."""
import heapq
import math
from typing import List, Dict, Any


INJURY_MULTIPLIER = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "none": 0
}


def build_rescue_items(victim_nodes: List[Dict], available_teams: List[Dict]) -> List[Dict]:
    """
    Convert victim nodes into knapsack items.
    weight = rescue_cost (estimated as distance from nearest team, normalized)
    value = survival_chance * people_stranded * injury_multiplier
    
    Args:
        victim_nodes: List of victim node dicts
        available_teams: List of available team dicts
    
    Returns:
        List of knapsack items
    """
    items = []
    for node in victim_nodes:
        people = node.get("people_stranded", 0)
        injury = node.get("injury_level", "none")
        survival = node.get("survival_chance", 1.0)
        
        # Calculate value based on urgency
        injury_mult = INJURY_MULTIPLIER.get(injury, 1)
        value = survival * people * injury_mult
        
        # Weight is proportional to people to rescue
        weight = max(1, people)
        
        items.append({
            "node_id": node.get("id"),
            "node_name": node.get("display_name", node.get("id")),
            "people": people,
            "injury_level": injury,
            "survival_chance": survival,
            "weight": weight,
            "value": value,
            "zone": node.get("zone", "")
        })
    
    return items


def knapsack_01(items: List[Dict], capacity: int) -> Dict:
    """
    Standard 0/1 Knapsack DP.
    
    Args:
        items: List of items with weight and value
        capacity: Maximum weight capacity
    
    Returns:
        dict: {
            "selected_items": list[dict],
            "not_selected": list[dict],
            "total_value": float,
            "total_weight": int,
            "capacity_used": int,
            "dp_table": list[list[int]],
            "items_count": int
        }
    """
    n = len(items)
    if n == 0 or capacity <= 0:
        return {
            "selected_items": [],
            "not_selected": [],
            "total_value": 0.0,
            "total_weight": 0,
            "capacity_used": 0,
            "dp_table": [[]],
            "items_count": 0
        }
    
    # Initialize DP table
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(1, n + 1):
        item = items[i - 1]
        weight = item["weight"]
        value = item["value"]
        
        for w in range(capacity + 1):
            if weight <= w:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - weight] + value)
            else:
                dp[i][w] = dp[i - 1][w]
    
    # Traceback to find selected items
    selected = []
    not_selected = []
    w = capacity
    
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(items[i - 1])
            w -= items[i - 1]["weight"]
        else:
            not_selected.append(items[i - 1])
    
    selected.reverse()
    
    total_value = dp[n][capacity]
    total_weight = sum(item["weight"] for item in selected)
    
    return {
        "selected_items": selected,
        "not_selected": not_selected,
        "total_value": total_value,
        "total_weight": total_weight,
        "capacity_used": total_weight,
        "dp_table": dp,
        "items_count": n
    }


def priority_queue_rescue_order(victim_nodes: List[Dict]) -> List[Dict]:
    """
    Use heapq (min-heap with negated priority) to order victims by urgency.
    Priority = survival_chance * -1 + injury_multiplier (lower survival = higher priority)
    
    Args:
        victim_nodes: List of victim node dicts
    
    Returns:
        Ordered list of victims (most urgent first)
    """
    heap = []
    
    for node in victim_nodes:
        people = node.get("people_stranded", 0)
        injury = node.get("injury_level", "none")
        survival = node.get("survival_chance", 1.0)
        
        injury_mult = INJURY_MULTIPLIER.get(injury, 1)
        
        # Priority score: lower survival and higher injury = higher priority
        # Use negative for max-heap behavior with min-heap
        priority = (1.0 - survival) * 10 + injury_mult
        
        heapq.heappush(heap, (-priority, node.get("id"), {
            "node_id": node.get("id"),
            "node_name": node.get("display_name", node.get("id")),
            "people": people,
            "injury_level": injury,
            "survival_chance": survival,
            "priority_score": priority
        }))
    
    # Extract in priority order
    ordered = []
    while heap:
        _, _, item = heapq.heappop(heap)
        ordered.append(item)
    
    return ordered
