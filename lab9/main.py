"""Демо: показывает, какие баги из примера получили флаг SLA."""
import sys
from datetime import datetime, timedelta, timezone

from sla import DEFAULT_SLA_DAYS, flag_bugs


def sample_bugs(now):
    def ago(days, hours=0):
        return now - timedelta(days=days, hours=hours)

    return [
        {"id": 1, "title": "Игра вылетает при открытии магазина", "priority": "critical", "status": "open", "updated_at": ago(5)},
        {"id": 2, "title": "Двойной клик создаёт два сохранения", "priority": "critical", "status": "in_progress", "updated_at": ago(1)},
        {"id": 3, "title": "Пропадает прогресс после обновления", "priority": "critical", "status": "closed", "updated_at": ago(20)},
        {"id": 4, "title": "Не начисляются монеты за рекламу", "priority": "high", "status": "open", "updated_at": ago(9)},
        {"id": 5, "title": "Не проходит оплата на iOS", "priority": "critical", "status": "fixed", "updated_at": ago(3)},
    ]


if __name__ == "__main__":
    # N можно передать аргументом: python main.py 5
    sla_days = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SLA_DAYS
    now = datetime.now(timezone.utc)
    flagged = flag_bugs(sample_bugs(now), now=now, sla_days=sla_days)

    print(f"Критичные баги без обновления {sla_days} дн. и больше:")
    for bug in flagged:
        days = (now - bug["updated_at"]).days
        print(f"  [FLAG] #{bug['id']} {bug['title']} ({bug['status']}, {days} дн. без обновления)")
    if not flagged:
        print("  нет")
