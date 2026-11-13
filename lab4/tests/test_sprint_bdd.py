# шаги для features/sprint.feature (pytest-bdd)
import pytest
from pytest_bdd import scenarios, given, when, then, parsers

from main import is_allowed, sum_sprint, within_capacity

scenarios("../features/sprint.feature")


@pytest.fixture
def context():
    # сюда шаги складывают результат, чтобы следующий шаг мог его проверить
    return {"points": [], "total": None, "error": None, "allowed": None}


@given(parsers.parse("в спринте задачи с оценками {points}"))
def sprint_with_points(context, points):
    context["points"] = [int(p) for p in points.split(",")]


@when("команда считает сумму спринта")
def count_sum(context):
    try:
        context["total"] = sum_sprint(context["points"])
    except ValueError as e:
        context["error"] = e


@when(parsers.parse("проверяют оценку {points:d}"))
def check_one_value(context, points):
    context["allowed"] = is_allowed(points)


@then(parsers.parse("сумма равна {expected:d}"))
def sum_is(context, expected):
    assert context["error"] is None
    assert context["total"] == expected


@then(parsers.parse("спринт помещается в capacity {capacity:d}"))
def sprint_fits(context, capacity):
    assert within_capacity(context["points"], capacity) is True


@then(parsers.parse("спринт не помещается в capacity {capacity:d}"))
def sprint_does_not_fit(context, capacity):
    assert within_capacity(context["points"], capacity) is False


@then("возникает ошибка ValueError")
def error_raised(context):
    assert isinstance(context["error"], ValueError)


@then(parsers.parse('оценка считается "{result}"'))
def value_is(context, result):
    assert context["allowed"] is (result == "допустимой")
