# main.py
from typing import Dict, List, Optional, Tuple


def register(candidates: Dict[str, int], name: str) -> None:
    if name in candidates:
        raise ValueError("already registered")
    candidates[name] = 0


def vote(candidates: Dict[str, int], name: str) -> None:
    if name not in candidates:
        raise KeyError("unknown candidate")
    candidates[name] += 1


def leader(candidates: Dict[str, int]) -> Optional[str]:
    if not candidates:
        return None
    best = max(candidates.values())
    leaders = [n for n, v in candidates.items() if v == best]
    if len(leaders) != 1:
        return None  # ничья или пусто по смыслу лидера
    return leaders[0]


def distribution_percent(candidates: Dict[str, int]) -> Dict[str, float]:
    total = sum(candidates.values())
    if total == 0:
        return {n: 0.0 for n in candidates}
    return {n: 100.0 * v / total for n, v in candidates.items()}


def is_tie(candidates: Dict[str, int]) -> bool:
    if len(candidates) < 2:
        return False
    best = max(candidates.values())
    return sum(1 for v in candidates.values() if v == best) > 1
