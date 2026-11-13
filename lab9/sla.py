"""Трекер багов: флаг SLA для критичных багов.

Правило: критичный баг, который не обновляли N дней, получает флаг.
"""
from datetime import datetime, timedelta, timezone

DEFAULT_SLA_DAYS = 3                      # N по умолчанию, можно передать своё

PRIORITIES = {"critical", "high", "medium", "low"}
ACTIVE_STATUSES = {"open", "in_progress", "fixed"}
DONE_STATUSES = {"verified", "closed"}    # по таким багам работа закончена, флаг не нужен


def to_utc(value, name):
    """Проверяет, что это время с часовым поясом, и переводит его в UTC."""
    if not isinstance(value, datetime):
        raise TypeError(f"{name} должно быть datetime, а не {type(value).__name__}")
    if value.utcoffset() is None:
        raise ValueError(f"{name} должно быть с часовым поясом")
    return value.astimezone(timezone.utc)


def is_sla_breached(bug, now, sla_days=DEFAULT_SLA_DAYS):
    """Возвращает True, если баг критичный и не обновлялся sla_days дней или дольше.

    bug  -- словарь с полями priority, status, updated_at
    now  -- текущее время (datetime с часовым поясом), передаётся снаружи,
            чтобы в тестах можно было подставить любое время
    """
    if isinstance(sla_days, bool) or not isinstance(sla_days, int) or sla_days <= 0:
        raise ValueError("sla_days должно быть целым числом больше 0")

    # сначала читаем и проверяем все поля, чтобы сломанный баг
    # давал ошибку при любом приоритете, а не только при critical
    priority = bug["priority"]
    status = bug["status"]
    if priority not in PRIORITIES:
        raise ValueError(f"неизвестный приоритет: {priority!r}")
    if status not in ACTIVE_STATUSES and status not in DONE_STATUSES:
        raise ValueError(f"неизвестный статус: {status!r}")

    # оба времени переводим в UTC. Без этого при одинаковом часовом поясе Python
    # вычитает "стенные" часы и ошибается на час в день перевода часов
    now = to_utc(now, "now")
    updated_at = to_utc(bug["updated_at"], "updated_at")

    if priority != "critical" or status in DONE_STATUSES:
        return False

    # сравниваем timedelta целиком, а не .days: иначе 3 дня 23 часа считались бы как 3 дня
    return now - updated_at >= timedelta(days=sla_days)


def flag_bugs(bugs, now=None, sla_days=DEFAULT_SLA_DAYS):
    """Возвращает список багов с флагом. Время берётся один раз на весь список."""
    if now is None:
        now = datetime.now(timezone.utc)
    return [bug for bug in bugs if is_sla_breached(bug, now, sla_days)]
