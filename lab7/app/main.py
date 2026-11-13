"""API трекера багов студии (Flask + PostgreSQL)."""
import os

import psycopg
from flask import Flask, jsonify, request
from psycopg.rows import dict_row

app = Flask(__name__)
app.json.ensure_ascii = False   # чтобы русский текст в ответах был читаемым

PRIORITIES = ["critical", "high", "medium", "low"]
STATUSES = ["open", "in_progress", "fixed", "verified", "closed"]


def get_connection():
    # настройки берутся из переменных окружения, их задаёт docker compose
    return psycopg.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        row_factory=dict_row,
    )


def error(message, code):
    return jsonify({"error": message}), code


@app.get("/health")
def health():
    """Проверка, что API живо и база отвечает."""
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
    except psycopg.Error:
        return jsonify({"status": "error", "db": "unavailable"}), 503
    return jsonify({"status": "ok", "db": "ok"})


@app.get("/bugs")
def list_bugs():
    """Список багов. Фильтры: ?priority=high и ?status=open."""
    priority = request.args.get("priority")
    status = request.args.get("status")
    if priority is not None and priority not in PRIORITIES:
        return error("priority должен быть одним из: " + ", ".join(PRIORITIES), 400)
    if status is not None and status not in STATUSES:
        return error("status должен быть одним из: " + ", ".join(STATUSES), 400)

    query = "SELECT * FROM bugs"
    conditions = []
    params = []
    if priority:
        conditions.append("priority = %s")
        params.append(priority)
    if status:
        conditions.append("status = %s")
        params.append(status)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY id"

    with get_connection() as conn:
        bugs = conn.execute(query, params).fetchall()
    return jsonify(bugs)


@app.get("/bugs/<int:bug_id>")
def get_bug(bug_id):
    with get_connection() as conn:
        bug = conn.execute("SELECT * FROM bugs WHERE id = %s", (bug_id,)).fetchone()
    if bug is None:
        return error("баг не найден", 404)
    return jsonify(bug)


@app.post("/bugs")
def create_bug():
    """Создать баг. Обязателен title, priority по умолчанию medium."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error("нужен JSON с полем title", 400)

    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    priority = data.get("priority", "medium")
    if not title:
        return error("поле title обязательно", 400)
    if len(title) > 200:
        return error("title длиннее 200 символов", 400)
    if priority not in PRIORITIES:
        return error("priority должен быть одним из: " + ", ".join(PRIORITIES), 400)

    with get_connection() as conn:
        bug = conn.execute(
            "INSERT INTO bugs (title, description, priority) VALUES (%s, %s, %s) RETURNING *",
            (title, description, priority),
        ).fetchone()
    return jsonify(bug), 201


@app.patch("/bugs/<int:bug_id>/status")
def change_status(bug_id):
    """Сменить статус бага: {"status": "fixed"}."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or data.get("status") not in STATUSES:
        return error("status должен быть одним из: " + ", ".join(STATUSES), 400)

    with get_connection() as conn:
        bug = conn.execute(
            "UPDATE bugs SET status = %s, updated_at = now() WHERE id = %s RETURNING *",
            (data["status"], bug_id),
        ).fetchone()
    if bug is None:
        return error("баг не найден", 404)
    return jsonify(bug)
