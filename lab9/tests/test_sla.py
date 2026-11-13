from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

from sla import DEFAULT_SLA_DAYS, flag_bugs, is_sla_breached

# фиксированное "сейчас": тесты не зависят от того, когда их запустили
NOW = datetime(2026, 11, 13, 12, 0, 0, tzinfo=timezone.utc)


def make_bug(priority="critical", status="open", **ago):
    """Баг, который обновляли ago назад: make_bug(days=3, hours=1)."""
    return {"id": 1, "priority": priority, "status": status, "updated_at": NOW - timedelta(**ago)}


# ---------- обычные случаи ----------

def test_fresh_critical_bug_has_no_flag():
    assert is_sla_breached(make_bug(days=0), NOW) is False


def test_old_critical_bug_has_flag():
    assert is_sla_breached(make_bug(days=10), NOW) is True


@pytest.mark.parametrize("priority", ["high", "medium", "low"])
def test_not_critical_bug_never_has_flag(priority):
    assert is_sla_breached(make_bug(priority=priority, days=100), NOW) is False


# ---------- граница N ----------

def test_border_exactly_n_days_has_flag():
    assert is_sla_breached(make_bug(days=3), NOW, sla_days=3) is True


def test_border_one_second_before_n_days_no_flag():
    bug = make_bug(days=3, seconds=-1)   # 2 дня 23:59:59
    assert is_sla_breached(bug, NOW, sla_days=3) is False


def test_border_one_second_after_n_days_has_flag():
    assert is_sla_breached(make_bug(days=3, seconds=1), NOW, sla_days=3) is True


@pytest.mark.parametrize("n", [1, 2, 7, 30])
def test_border_for_different_n(n):
    assert is_sla_breached(make_bug(days=n), NOW, sla_days=n) is True
    assert is_sla_breached(make_bug(days=n, seconds=-1), NOW, sla_days=n) is False


def test_default_n_is_used():
    assert is_sla_breached(make_bug(days=DEFAULT_SLA_DAYS), NOW) is True
    assert is_sla_breached(make_bug(days=DEFAULT_SLA_DAYS, seconds=-1), NOW) is False


def test_same_bug_depends_on_n():
    bug = make_bug(days=4)
    assert is_sla_breached(bug, NOW, sla_days=3) is True
    assert is_sla_breached(bug, NOW, sla_days=5) is False


# ---------- статусы ----------

@pytest.mark.parametrize("status", ["open", "in_progress", "fixed"])
def test_active_statuses_get_flag(status):
    assert is_sla_breached(make_bug(status=status, days=10), NOW) is True


@pytest.mark.parametrize("status", ["verified", "closed"])
def test_done_statuses_never_get_flag(status):
    assert is_sla_breached(make_bug(status=status, days=10), NOW) is False


# ---------- время ----------

def test_update_in_future_no_flag():
    # часы на сервере и у клиента могут расходиться
    assert is_sla_breached(make_bug(days=-1), NOW) is False


def test_other_timezone_is_compared_correctly():
    minsk = timezone(timedelta(hours=3))
    bug = make_bug(days=3)
    bug["updated_at"] = bug["updated_at"].astimezone(minsk)
    assert is_sla_breached(bug, NOW, sla_days=3) is True


def test_time_without_timezone_raises_error():
    bug = make_bug(days=10)
    bug["updated_at"] = bug["updated_at"].replace(tzinfo=None)
    with pytest.raises(ValueError):
        is_sla_breached(bug, NOW)
    with pytest.raises(ValueError):
        is_sla_breached(make_bug(days=10), NOW.replace(tzinfo=None))


# ---------- неправильные входные данные ----------

@pytest.mark.parametrize("bad_n", [0, -1, 2.5, "3", True, None])
def test_bad_n_raises_error(bad_n):
    with pytest.raises(ValueError):
        is_sla_breached(make_bug(days=10), NOW, sla_days=bad_n)


def test_bug_without_field_raises_key_error():
    with pytest.raises(KeyError):
        is_sla_breached({"priority": "critical", "status": "open"}, NOW)


# ---------- flag_bugs ----------

def test_flag_bugs_returns_only_flagged():
    bugs = [
        make_bug(days=10),
        make_bug(priority="low", days=10),
        make_bug(days=1),
        make_bug(status="closed", days=10),
    ]
    assert flag_bugs(bugs, now=NOW) == [bugs[0]]


def test_flag_bugs_empty_list():
    assert flag_bugs([], now=NOW) == []


def test_flag_bugs_passes_n():
    bugs = [make_bug(days=4)]
    assert flag_bugs(bugs, now=NOW, sla_days=3) == bugs
    assert flag_bugs(bugs, now=NOW, sla_days=5) == []


def test_flag_bugs_without_now_uses_current_time():
    old = {"id": 1, "priority": "critical", "status": "open",
           "updated_at": datetime(2020, 1, 1, tzinfo=timezone.utc)}
    assert flag_bugs([old]) == [old]


def test_flag_bugs_does_not_change_input():
    bugs = [make_bug(days=10)]
    copy = [dict(b) for b in bugs]
    flag_bugs(bugs, now=NOW)
    assert bugs == copy


# ---------- случаи после повторной проверки ревью ----------

def test_updated_hour_ago_with_n_1_no_flag():
    # баг обновили час назад, N = 1: до суток ещё далеко
    assert is_sla_breached(make_bug(hours=1), NOW, sla_days=1) is False


@pytest.mark.parametrize("ago, expected", [
    ({"seconds": 0}, False),                                # обновили только что
    ({"hours": 12}, False),                                 # полсуток
    ({"hours": 23, "minutes": 59, "seconds": 59}, False),   # секунда до суток
    ({"hours": 24}, True),                                  # ровно сутки
    ({"hours": 25}, True),
])
def test_n_1_in_hours(ago, expected):
    assert is_sla_breached(make_bug(**ago), NOW, sla_days=1) is expected


def test_hours_do_not_round_up_to_days():
    # 2 дня 23 часа при N = 3: почти три дня, но флага ещё нет
    assert is_sla_breached(make_bug(days=2, hours=23), NOW, sla_days=3) is False


def test_clock_change_in_autumn_real_time_is_used():
    # 25.10.2026 в Варшаве часы переводят на час назад.
    # По "стенным" часам прошло 23:30, на самом деле 24:30
    warsaw = ZoneInfo("Europe/Warsaw")
    bug = make_bug()
    bug["updated_at"] = datetime(2026, 10, 24, 12, 0, tzinfo=warsaw)
    now = datetime(2026, 10, 25, 11, 30, tzinfo=warsaw)
    assert is_sla_breached(bug, now, sla_days=1) is True


def test_clock_change_in_spring_real_time_is_used():
    # 29.03.2026 часы переводят вперёд: по "стенным" часам сутки, на самом деле 23 часа
    warsaw = ZoneInfo("Europe/Warsaw")
    bug = make_bug()
    bug["updated_at"] = datetime(2026, 3, 28, 12, 0, tzinfo=warsaw)
    now = datetime(2026, 3, 29, 12, 0, tzinfo=warsaw)
    assert is_sla_breached(bug, now, sla_days=1) is False


@pytest.mark.parametrize("bad_time", ["2026-11-01T10:00:00+00:00", None, 1762000000])
def test_time_must_be_datetime(bad_time):
    bug = make_bug(days=10)
    bug["updated_at"] = bad_time
    with pytest.raises(TypeError):
        is_sla_breached(bug, NOW)
    with pytest.raises(TypeError):
        is_sla_breached(make_bug(days=10), bad_time)


@pytest.mark.parametrize("status", ["Closed", "wontfix", "", None])
def test_unknown_status_raises_error(status):
    # раньше баг с опечаткой в статусе молча получал флаг
    with pytest.raises(ValueError):
        is_sla_breached(make_bug(status=status, days=10), NOW)


@pytest.mark.parametrize("priority", ["Critical", "urgent", "", None])
def test_unknown_priority_raises_error(priority):
    # раньше "Critical" с большой буквы молча оставался без флага
    with pytest.raises(ValueError):
        is_sla_breached(make_bug(priority=priority, days=10), NOW)


@pytest.mark.parametrize("priority", ["critical", "low"])
@pytest.mark.parametrize("field", ["priority", "status", "updated_at"])
def test_missing_field_raises_key_error_for_any_priority(priority, field):
    bug = make_bug(priority=priority, days=10)
    del bug[field]
    with pytest.raises(KeyError):
        is_sla_breached(bug, NOW)


def test_flag_bugs_keeps_order_and_same_objects():
    bugs = [make_bug(days=10), make_bug(days=1), make_bug(days=5)]
    bugs[0]["id"], bugs[1]["id"], bugs[2]["id"] = 3, 1, 2
    result = flag_bugs(bugs, now=NOW)
    assert [b["id"] for b in result] == [3, 2]
    assert result[0] is bugs[0]


def test_flag_bugs_accepts_generator():
    bugs = [make_bug(days=10)]
    assert flag_bugs((b for b in bugs), now=NOW) == bugs


def test_flag_bugs_one_broken_bug_raises_error():
    # сломанный баг не пропускается молча
    broken = make_bug(days=10)
    del broken["updated_at"]
    with pytest.raises(KeyError):
        flag_bugs([make_bug(days=10), broken], now=NOW)
