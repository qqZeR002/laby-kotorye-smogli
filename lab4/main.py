# main.py
ALLOWED = {1, 2, 3, 5, 8, 13}


def is_allowed(points: int) -> bool:
    # True == 1 в Python, поэтому bool отсекаем отдельно
    if isinstance(points, bool) or not isinstance(points, int):
        return False
    return points in ALLOWED


def sum_sprint(points_list: list[int]) -> int:
    """Если есть значение вне ALLOWED — ValueError."""
    for p in points_list:
        if not is_allowed(p):
            raise ValueError(f"недопустимая оценка: {p!r}")
    return sum(points_list)


def within_capacity(points_list: list[int], capacity: int) -> bool:
    if capacity < 0:
        raise ValueError("capacity не может быть отрицательной")
    return sum_sprint(points_list) <= capacity
