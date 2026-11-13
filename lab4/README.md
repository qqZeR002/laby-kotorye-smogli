# Задача 19: Оценка сложности задачи (story points)

**Студент:** Ленец Е.

**Постановка.** Реализуйте:

```python
# main.py
ALLOWED = {1, 2, 3, 5, 8, 13}

def is_allowed(points: int) -> bool:
    ...

def sum_sprint(points_list: list[int]) -> int:
    """Если есть значение вне ALLOWED — ValueError."""
    ...

def within_capacity(points_list: list[int], capacity: int) -> bool:
    ...
```

BDD: валидный спринт, недопустимые points, перегруз capacity.

## Структура

| Файл | Что это |
|------|---------|
| `main.py` | три функции из постановки |
| `tests/test_main.py` | юнит-тесты (pytest), 30 проверок |
| `features/sprint.feature` | BDD-сценарии на Gherkin (на русском), 5 сценариев |
| `tests/test_sprint_bdd.py` | шаги к сценариям (pytest-bdd) |
| `pytest.ini` | настройки pytest |

## Установка

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск юнит-тестов

```bash
pytest tests/test_main.py -v
```

## Запуск BDD

```bash
pytest tests/test_sprint_bdd.py -v
```

Всё сразу: `pytest -v` (38 passed).

Сценарии в `features/sprint.feature`:

1. Валидный спринт помещается в capacity (3 + 5 + 8 = 16, capacity 20).
2. Спринт ровно на границе capacity (18 из 18).
3. Недопустимые points (оценка 4) — `ValueError`.
4. Проверка одной оценки (структура сценария с таблицей примеров).
5. Перегруз capacity (29 при capacity 25).

## Как ведут себя функции

- `is_allowed(points)` возвращает `True` только для целых 1, 2, 3, 5, 8, 13. Для `True`, `1.0`, `"5"`, `None` возвращает `False`.
- `sum_sprint(points_list)` возвращает сумму. Если в списке есть недопустимое значение, выбрасывает `ValueError`. Пустой список даёт 0.
- `within_capacity(points_list, capacity)` возвращает `True`, если сумма меньше или равна capacity. Недопустимые points или отрицательная capacity дают `ValueError`.

## Red–Green–Refactor (кратко)

Каждый шаг — отдельный коммит, их видно в истории (`git log --oneline`).

**1. Red.** Сначала написал тесты и сценарии, а в `main.py` оставил каркас с `...` из задания. Функции возвращали `None`, поэтому результат был такой:

```
31 failed, 1 passed
```

(прошёл только тест, который проверяет само множество `ALLOWED`). Например, `test_sum_sprint_simple` падал с `assert None == 6`.

**2. Green.** Написал самую простую реализацию, чтобы тесты прошли: `is_allowed` через `in ALLOWED`, в `sum_sprint` цикл с проверкой и суммой. В `within_capacity` на этом шаге я просто скопировал тот же цикл.

```
32 passed
```

**3. Refactor.** Тесты зелёные, поэтому код можно менять спокойно:

- убрал дублирование: `within_capacity` теперь вызывает `sum_sprint`, а `sum_sprint` — `is_allowed`;
- заметил, что `True in {1, 2, 3}` в Python даёт `True`, то есть `sum_sprint([True, 2])` проходил бы как валидный спринт. Сначала добавил тест на это (он упал), потом добавил проверку типа в `is_allowed`;
- добавил `ValueError` для отрицательной capacity (тоже сначала тест).

```
38 passed
```

На втором и третьем пункте рефакторинга цикл повторился в малом виде: тест → красный → правка → зелёный.
