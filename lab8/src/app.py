"""Stub API трекера багов: данные хранятся в памяти и пропадают при перезапуске.

Нужен, чтобы можно было открыть Swagger UI и попробовать запросы из openapi.yaml.
"""
import os
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request, send_file

app = Flask(__name__)
app.json.ensure_ascii = False

SPEC_FILE = Path(__file__).resolve().parent.parent / "openapi.yaml"

PRIORITIES = ["critical", "high", "medium", "low"]
STATUSES = ["open", "in_progress", "fixed", "verified", "closed"]
# из какого статуса в какой можно перейти
TRANSITIONS = {
    "open": ["in_progress"],
    "in_progress": ["fixed"],
    "fixed": ["verified", "in_progress"],
    "verified": ["closed"],
    "closed": [],
}

issues = {}     # id -> баг
next_id = 1


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def error(message, code):
    return jsonify({"error": message}), code


def read_issue_fields():
    """Достаёт и проверяет поля из тела запроса. Возвращает (поля, текст ошибки)."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None, "нужен JSON"
    title = str(data.get("title", "")).strip()
    if not title:
        return None, "поле title обязательно"
    if len(title) > 200:
        return None, "title длиннее 200 символов"
    priority = data.get("priority", "medium")
    if priority not in PRIORITIES:
        return None, "priority должен быть одним из: " + ", ".join(PRIORITIES)
    fields = {
        "title": title,
        "description": str(data.get("description", "")),
        "priority": priority,
        "assignee": data.get("assignee"),
    }
    return fields, None


def add_issue(fields, status="open"):
    global next_id
    issue = {"id": next_id, **fields, "status": status, "created_at": now(), "updated_at": now()}
    issues[next_id] = issue
    next_id += 1
    return issue


@app.get("/issues")
def list_issues():
    priority = request.args.get("priority")
    status = request.args.get("status")
    if priority is not None and priority not in PRIORITIES:
        return error("priority должен быть одним из: " + ", ".join(PRIORITIES), 400)
    if status is not None and status not in STATUSES:
        return error("status должен быть одним из: " + ", ".join(STATUSES), 400)
    result = []
    for issue in issues.values():
        if priority and issue["priority"] != priority:
            continue
        if status and issue["status"] != status:
            continue
        result.append(issue)
    return jsonify(result)


@app.post("/issues")
def create_issue():
    fields, message = read_issue_fields()
    if message:
        return error(message, 400)
    return jsonify(add_issue(fields)), 201


@app.get("/issues/<int:issue_id>")
def get_issue(issue_id):
    if issue_id not in issues:
        return error("баг не найден", 404)
    return jsonify(issues[issue_id])


@app.put("/issues/<int:issue_id>")
def update_issue(issue_id):
    if issue_id not in issues:
        return error("баг не найден", 404)
    fields, message = read_issue_fields()
    if message:
        return error(message, 400)
    issues[issue_id].update(fields)
    issues[issue_id]["updated_at"] = now()
    return jsonify(issues[issue_id])


@app.delete("/issues/<int:issue_id>")
def delete_issue(issue_id):
    if issue_id not in issues:
        return error("баг не найден", 404)
    del issues[issue_id]
    return "", 204


@app.patch("/issues/<int:issue_id>/status")
def change_status(issue_id):
    if issue_id not in issues:
        return error("баг не найден", 404)
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or data.get("status") not in STATUSES:
        return error("status должен быть одним из: " + ", ".join(STATUSES), 400)
    old = issues[issue_id]["status"]
    new = data["status"]
    if new not in TRANSITIONS[old]:
        return error(f"нельзя перейти из {old} в {new}", 409)
    issues[issue_id]["status"] = new
    issues[issue_id]["updated_at"] = now()
    return jsonify(issues[issue_id])


# ---------- документация ----------

@app.get("/openapi.yaml")
def spec():
    return send_file(SPEC_FILE, mimetype="application/yaml")


@app.get("/docs")
def docs():
    """Swagger UI, сам интерфейс подгружается с CDN."""
    return """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>Трекер багов: API</title>
<link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>
SwaggerUIBundle({url: "/openapi.yaml", dom_id: "#swagger-ui"});
</script>
</body>
</html>"""


# несколько багов для примера, чтобы список не был пустым
add_issue({"title": "Игра вылетает при открытии магазина", "description": "Android 14, версия 1.4.2",
           "priority": "critical", "assignee": "igor"})
add_issue({"title": "Не начисляются монеты за рекламу", "description": "Баланс меняется только после перезахода",
           "priority": "high", "assignee": None})
add_issue({"title": "Опечатка в описании уровня 7", "description": "«собирите» вместо «соберите»",
           "priority": "low", "assignee": "oleg"}, status="fixed")


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", "8000")))
