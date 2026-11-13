"""Задача 19: Голосование. ООП-стиль.

Candidate отвечает за свои голоса, Election — за список кандидатов
и подсчёт результатов. Состояние спрятано внутри объектов.
"""
import sys


class Candidate:
    def __init__(self, name):
        self._name = name
        self._votes = 0

    @property
    def name(self):
        return self._name

    @property
    def votes(self):
        return self._votes

    def add_vote(self):
        self._votes += 1


class Election:
    def __init__(self):
        self._candidates = {}   # имя -> Candidate

    def register(self, name):
        name = name.strip()
        if not name:
            raise ValueError("имя кандидата не может быть пустым")
        if name in self._candidates:
            raise ValueError(f"кандидат «{name}» уже зарегистрирован")
        self._candidates[name] = Candidate(name)

    def vote(self, name):
        name = name.strip()
        if name not in self._candidates:
            raise KeyError(f"кандидат «{name}» не зарегистрирован")
        self._candidates[name].add_vote()

    def total_votes(self):
        return sum(c.votes for c in self._candidates.values())

    def leaders(self):
        """Все кандидаты с максимальным числом голосов."""
        if not self._candidates:
            return []
        best = max(c.votes for c in self._candidates.values())
        return [c.name for c in self._candidates.values() if c.votes == best]

    def leader(self):
        """Имя лидера или None, если кандидатов нет или у лидеров ничья."""
        leaders = self.leaders()
        return leaders[0] if len(leaders) == 1 else None

    def is_tie(self):
        return len(self.leaders()) > 1

    def distribution_percent(self):
        total = self.total_votes()
        if total == 0:
            return {name: 0.0 for name in self._candidates}
        return {c.name: 100.0 * c.votes / total for c in self._candidates.values()}

    def print_results(self):
        percents = self.distribution_percent()
        print(f"  Всего голосов: {self.total_votes()}")
        for c in self._candidates.values():
            print(f"  {c.name:<10} {c.votes:>3} гол.  {percents[c.name]:5.1f} %")
        if self.leader() is not None:
            print(f"  Лидер: {self.leader()}")
        elif self.is_tie():
            print("  Ничья между: " + ", ".join(self.leaders()))
        else:
            print("  Лидера нет: нет кандидатов")


class ConsoleApp:
    """Отвечает только за общение с пользователем, логика — в Election."""

    def __init__(self):
        self.election = Election()

    def run_demo(self):
        print("=== Демо: ООП-стиль ===")
        e = self.election

        print("\n1. Регистрация кандидатов: Анна, Борис, Вера")
        for name in ["Анна", "Борис", "Вера"]:
            e.register(name)
        e.print_results()

        print("\n2. Голоса: Анна, Борис, Анна, Вера, Борис")
        for name in ["Анна", "Борис", "Анна", "Вера", "Борис"]:
            e.vote(name)
        e.print_results()

        print("\n3. Ещё один голос за Анну")
        e.vote("Анна")
        e.print_results()

        print("\n4. Ошибки")
        try:
            e.register("Анна")
        except ValueError as err:
            print("  Повторная регистрация:", err)
        try:
            e.vote("Глеб")
        except KeyError as err:
            print("  Голос за незарегистрированного:", err.args[0])

        print("\n5. Пустое голосование")
        Election().print_results()

    def run_interactive(self):
        print("Команды: add <имя>, vote <имя>, show, exit")
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break
            command, _, arg = line.partition(" ")
            try:
                if command == "add":
                    self.election.register(arg)
                    print("  зарегистрирован:", arg.strip())
                elif command == "vote":
                    self.election.vote(arg)
                    print("  голос принят")
                elif command == "show":
                    self.election.print_results()
                elif command == "exit":
                    break
                elif command:
                    print("  неизвестная команда")
            except ValueError as err:
                print("  ошибка:", err)
            except KeyError as err:
                print("  ошибка:", err.args[0])


if __name__ == "__main__":
    app = ConsoleApp()
    if "-i" in sys.argv:
        app.run_interactive()
    else:
        app.run_demo()
