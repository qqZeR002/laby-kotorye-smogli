"""Задача 19: Голосование. Структурный стиль.

Данные (словарь кандидатов) хранятся отдельно, вся логика — в функциях,
которые получают этот словарь параметром.
"""
import sys


def create_election():
    """Новое голосование: словарь {имя кандидата: число голосов}."""
    return {}


def register_candidate(candidates, name):
    name = name.strip()
    if not name:
        raise ValueError("имя кандидата не может быть пустым")
    if name in candidates:
        raise ValueError(f"кандидат «{name}» уже зарегистрирован")
    candidates[name] = 0


def cast_vote(candidates, name):
    name = name.strip()
    if name not in candidates:
        raise KeyError(f"кандидат «{name}» не зарегистрирован")
    candidates[name] += 1


def total_votes(candidates):
    return sum(candidates.values())


def find_leaders(candidates):
    """Все кандидаты с максимальным числом голосов (их может быть несколько)."""
    if not candidates:
        return []
    best = max(candidates.values())
    return [name for name, votes in candidates.items() if votes == best]


def get_leader(candidates):
    """Имя лидера или None, если кандидатов нет или у лидеров ничья."""
    leaders = find_leaders(candidates)
    if len(leaders) != 1:
        return None
    return leaders[0]


def is_tie(candidates):
    """Ничья: максимальное число голосов у двух и более кандидатов."""
    return len(find_leaders(candidates)) > 1


def distribution_percent(candidates):
    """Доля голосов каждого кандидата в процентах."""
    total = total_votes(candidates)
    if total == 0:
        return {name: 0.0 for name in candidates}
    return {name: 100.0 * votes / total for name, votes in candidates.items()}


def print_results(candidates):
    percents = distribution_percent(candidates)
    print(f"  Всего голосов: {total_votes(candidates)}")
    for name, votes in candidates.items():
        print(f"  {name:<10} {votes:>3} гол.  {percents[name]:5.1f} %")
    leader = get_leader(candidates)
    if leader is not None:
        print(f"  Лидер: {leader}")
    elif is_tie(candidates):
        print("  Ничья между: " + ", ".join(find_leaders(candidates)))
    else:
        print("  Лидера нет: нет кандидатов")


def run_demo():
    print("=== Демо: структурный стиль ===")
    election = create_election()

    print("\n1. Регистрация кандидатов: Анна, Борис, Вера")
    for name in ["Анна", "Борис", "Вера"]:
        register_candidate(election, name)
    print_results(election)

    print("\n2. Голоса: Анна, Борис, Анна, Вера, Борис")
    for name in ["Анна", "Борис", "Анна", "Вера", "Борис"]:
        cast_vote(election, name)
    print_results(election)

    print("\n3. Ещё один голос за Анну")
    cast_vote(election, "Анна")
    print_results(election)

    print("\n4. Ошибки")
    try:
        register_candidate(election, "Анна")
    except ValueError as e:
        print("  Повторная регистрация:", e)
    try:
        cast_vote(election, "Глеб")
    except KeyError as e:
        print("  Голос за незарегистрированного:", e.args[0])

    print("\n5. Пустое голосование")
    print_results(create_election())


def run_interactive():
    election = create_election()
    print("Команды: add <имя>, vote <имя>, show, exit")
    while True:
        try:
            line = input("> ").strip()
        except EOFError:
            break
        command, _, arg = line.partition(" ")
        try:
            if command == "add":
                register_candidate(election, arg)
                print("  зарегистрирован:", arg.strip())
            elif command == "vote":
                cast_vote(election, arg)
                print("  голос принят")
            elif command == "show":
                print_results(election)
            elif command == "exit":
                break
            elif command:
                print("  неизвестная команда")
        except ValueError as e:
            print("  ошибка:", e)
        except KeyError as e:
            print("  ошибка:", e.args[0])


if __name__ == "__main__":
    if "-i" in sys.argv:
        run_interactive()
    else:
        run_demo()
