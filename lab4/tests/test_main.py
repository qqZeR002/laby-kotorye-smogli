import pytest

from main import ALLOWED, is_allowed, sum_sprint, within_capacity


# ---------- is_allowed ----------

@pytest.mark.parametrize("points", [1, 2, 3, 5, 8, 13])
def test_is_allowed_for_fibonacci_values(points):
    assert is_allowed(points) is True


@pytest.mark.parametrize("points", [0, 4, 6, 7, 21, -1, 100])
def test_is_allowed_false_for_other_numbers(points):
    assert is_allowed(points) is False


def test_allowed_set_is_not_changed():
    assert ALLOWED == {1, 2, 3, 5, 8, 13}


# ---------- sum_sprint ----------

def test_sum_sprint_simple():
    assert sum_sprint([1, 2, 3]) == 6


def test_sum_sprint_empty_list_is_zero():
    assert sum_sprint([]) == 0


def test_sum_sprint_with_repeats():
    assert sum_sprint([5, 5, 8]) == 18


def test_sum_sprint_invalid_value_raises_error():
    with pytest.raises(ValueError):
        sum_sprint([1, 4, 3])


def test_sum_sprint_error_even_if_invalid_is_last():
    with pytest.raises(ValueError):
        sum_sprint([13, 8, 0])


# ---------- within_capacity ----------

def test_within_capacity_fits():
    assert within_capacity([3, 5, 8], 20) is True


def test_within_capacity_exactly_equal():
    # ровно в capacity — ещё помещается
    assert within_capacity([5, 5, 8], 18) is True


def test_within_capacity_overload_by_one():
    assert within_capacity([5, 5, 8], 17) is False


def test_within_capacity_empty_sprint():
    assert within_capacity([], 0) is True


def test_within_capacity_invalid_points_raises_error():
    with pytest.raises(ValueError):
        within_capacity([3, 4], 100)


# ---------- добавлено на шаге refactor ----------

@pytest.mark.parametrize("value", [True, 1.0, "5", None])
def test_is_allowed_false_for_not_int(value):
    assert is_allowed(value) is False


def test_sum_sprint_rejects_true_as_points():
    with pytest.raises(ValueError):
        sum_sprint([True, 2])


def test_within_capacity_negative_capacity_raises_error():
    with pytest.raises(ValueError):
        within_capacity([1], -5)
