#!/usr/bin/env python3
"""Local API for the OSM checking practice mockup.

This is deliberately small: SQLite for storage and Python's standard library for
HTTP. It is useful for demos, database planning, and frontend wiring, but it is
not a production exam-evaluation service.
"""

from __future__ import annotations

import json
import sqlite3
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "osm_mock.db"
SCHEMA_PATH = ROOT / "schema.sql"

API_HOST = "127.0.0.1"
API_PORT = 8080
DEMO_EVALUATOR_EMAIL = "evaluator@example.test"

DEMO_BUNDLE = {
    "subject": "Mathematics",
    "exam_code": "DEMO-MATH-001",
    "due_at": "2026-06-15T18:00:00Z",
}

DEMO_SCRIPTS = [
    {"roll": "248315", "pages": 12, "status": "checking", "question": 3},
    {"roll": "248426", "pages": 10, "status": "submitted", "question": 5},
    {"roll": "248599", "pages": 14, "status": "flagged", "question": 2},
    {"roll": "248712", "pages": 11, "status": "queued", "question": 6},
]

DEMO_QUESTIONS = [
    ("Q1", 5, "Award method marks and final answer marks separately."),
    ("Q2", 5, "Check formula selection, substitution, and simplification."),
    ("Q3", 5, "Give partial credit for correct steps even if final unit is missing."),
    ("Q4", 5, "Verify diagram labels before awarding construction marks."),
    ("Q5", 5, "Award reasoning marks only when conclusion follows from working."),
]


def connect() -> sqlite3.Connection:
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def as_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def initialize_database() -> None:
    with connect() as db:
        db.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        seed_database(db)


def seed_database(db: sqlite3.Connection) -> None:
    evaluator_id = upsert_demo_evaluator(db)
    bundle_id = upsert_demo_bundle(db, evaluator_id)
    seed_scripts(db, bundle_id)
    seed_questions(db)
    seed_script_pages(db)


def upsert_demo_evaluator(db: sqlite3.Connection) -> int:
    row = db.execute(
        """
        INSERT INTO users (name, email, role)
        VALUES (?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET name = excluded.name
        RETURNING id
        """,
        ("Demo Evaluator", DEMO_EVALUATOR_EMAIL, "evaluator"),
    ).fetchone()
    return int(row["id"])


def upsert_demo_bundle(db: sqlite3.Connection, evaluator_id: int) -> int:
    row = db.execute(
        """
        INSERT INTO script_bundles (subject, exam_code, status, assigned_to, due_at)
        SELECT ?, ?, 'in_progress', ?, ?
        WHERE NOT EXISTS (SELECT 1 FROM script_bundles WHERE exam_code = ?)
        RETURNING id
        """,
        (
            DEMO_BUNDLE["subject"],
            DEMO_BUNDLE["exam_code"],
            evaluator_id,
            DEMO_BUNDLE["due_at"],
            DEMO_BUNDLE["exam_code"],
        ),
    ).fetchone()

    if row is None:
        row = db.execute(
            "SELECT id FROM script_bundles WHERE exam_code = ?",
            (DEMO_BUNDLE["exam_code"],),
        ).fetchone()

    return int(row["id"])


def seed_scripts(db: sqlite3.Connection, bundle_id: int) -> None:
    records = [
        (bundle_id, script["roll"], script["pages"], script["status"], script["question"])
        for script in DEMO_SCRIPTS
    ]
    db.executemany(
        """
        INSERT OR IGNORE INTO answer_scripts
          (bundle_id, masked_roll_no, page_count, status, current_question)
        VALUES (?, ?, ?, ?, ?)
        """,
        records,
    )


def seed_questions(db: sqlite3.Connection) -> None:
    records = [
        (DEMO_BUNDLE["subject"], question_no, max_marks, rubric)
        for question_no, max_marks, rubric in DEMO_QUESTIONS
    ]
    db.executemany(
        """
        INSERT INTO questions (subject, question_no, max_marks, rubric)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(subject, question_no) DO UPDATE SET
          max_marks = excluded.max_marks,
          rubric = excluded.rubric
        """,
        records,
    )


def seed_script_pages(db: sqlite3.Connection) -> None:
    scripts = db.execute("SELECT id, page_count FROM answer_scripts").fetchall()

    for script in scripts:
        pages = [
            (script["id"], page_number, f"/demo-pages/script-{script['id']}/page-{page_number:02}.png")
            for page_number in range(1, script["page_count"] + 1)
        ]
        db.executemany(
            """
            INSERT OR IGNORE INTO script_pages (script_id, page_number, image_url)
            VALUES (?, ?, ?)
            """,
            pages,
        )


def demo_evaluator_id(db: sqlite3.Connection) -> int:
    row = db.execute(
        "SELECT id FROM users WHERE email = ?",
        (DEMO_EVALUATOR_EMAIL,),
    ).fetchone()

    if row is None:
        raise RuntimeError("The demo evaluator has not been seeded")

    return int(row["id"])


def list_scripts() -> list[dict]:
    with connect() as db:
        rows = db.execute(
            """
            SELECT
              answer_scripts.id,
              answer_scripts.masked_roll_no,
              answer_scripts.page_count,
              answer_scripts.status,
              answer_scripts.current_question,
              answer_scripts.total_awarded,
              script_bundles.subject,
              script_bundles.exam_code
            FROM answer_scripts
            JOIN script_bundles ON script_bundles.id = answer_scripts.bundle_id
            ORDER BY answer_scripts.id
            """
        ).fetchall()
        return [as_dict(row) for row in rows]


def get_script(script_id: int) -> dict | None:
    with connect() as db:
        script = find_script(db, script_id)
        if script is None:
            return None

        evaluation = ensure_evaluation(db, script_id)
        payload = as_dict(script)
        payload["pages"] = list_pages(db, script_id)
        payload["questions"] = list_questions(db, script["subject"])
        payload["evaluation"] = as_dict(evaluation)
        payload["marks"] = list_marks(db, evaluation["id"])
        return payload


def find_script(db: sqlite3.Connection, script_id: int) -> sqlite3.Row | None:
    return db.execute(
        """
        SELECT
          answer_scripts.*,
          script_bundles.subject,
          script_bundles.exam_code
        FROM answer_scripts
        JOIN script_bundles ON script_bundles.id = answer_scripts.bundle_id
        WHERE answer_scripts.id = ?
        """,
        (script_id,),
    ).fetchone()


def list_pages(db: sqlite3.Connection, script_id: int) -> list[dict]:
    rows = db.execute(
        "SELECT page_number, image_url FROM script_pages WHERE script_id = ? ORDER BY page_number",
        (script_id,),
    ).fetchall()
    return [as_dict(row) for row in rows]


def list_questions(db: sqlite3.Connection, subject: str) -> list[dict]:
    rows = db.execute(
        "SELECT id, question_no, max_marks, rubric FROM questions WHERE subject = ? ORDER BY id",
        (subject,),
    ).fetchall()
    return [as_dict(row) for row in rows]


def list_marks(db: sqlite3.Connection, evaluation_id: int) -> list[dict]:
    rows = db.execute(
        """
        SELECT questions.question_no, questions.max_marks, marks.awarded_marks, marks.comment
        FROM marks
        JOIN questions ON questions.id = marks.question_id
        WHERE marks.evaluation_id = ?
        ORDER BY questions.id
        """,
        (evaluation_id,),
    ).fetchall()
    return [as_dict(row) for row in rows]


def ensure_evaluation(db: sqlite3.Connection, script_id: int) -> sqlite3.Row:
    evaluator_id = demo_evaluator_id(db)
    existing = db.execute(
        "SELECT * FROM evaluations WHERE script_id = ? AND evaluator_id = ?",
        (script_id, evaluator_id),
    ).fetchone()

    if existing is not None:
        return existing

    return db.execute(
        """
        INSERT INTO evaluations (script_id, evaluator_id, status)
        VALUES (?, ?, 'draft')
        RETURNING *
        """,
        (script_id, evaluator_id),
    ).fetchone()


def save_marks(script_id: int, marks: list[dict], remarks: str) -> dict | None:
    with connect() as db:
        script = find_script(db, script_id)
        if script is None:
            return None

        evaluation = ensure_evaluation(db, script_id)
        questions = questions_by_number(db, script["subject"])

        for mark in marks:
            save_single_mark(db, evaluation["id"], questions, mark)

        total = total_awarded(db, evaluation["id"])
        db.execute(
            """
            UPDATE evaluations
            SET remarks = ?, status = 'draft', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (remarks, evaluation["id"]),
        )
        db.execute(
            """
            UPDATE answer_scripts
            SET total_awarded = ?, status = 'draft_saved', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (total, script_id),
        )
        write_audit_event(
            db,
            script_id,
            "marks_saved",
            {"total_awarded": total, "questions_saved": len(marks)},
        )
        db.commit()

    return get_script(script_id)


def questions_by_number(db: sqlite3.Connection, subject: str) -> dict[str, sqlite3.Row]:
    rows = db.execute(
        "SELECT id, question_no, max_marks FROM questions WHERE subject = ? ORDER BY id",
        (subject,),
    ).fetchall()
    return {row["question_no"].upper(): row for row in rows}


def save_single_mark(
    db: sqlite3.Connection,
    evaluation_id: int,
    questions: dict[str, sqlite3.Row],
    mark: dict,
) -> None:
    question_no = str(mark.get("question_no", "")).strip().upper()
    question = questions.get(question_no)

    if question is None:
        raise ValueError(f"Unknown question: {question_no or 'blank'}")

    awarded = float(mark.get("awarded_marks", 0))
    if awarded < 0 or awarded > question["max_marks"]:
        raise ValueError(f"Marks for {question_no} must be between 0 and {question['max_marks']}")

    db.execute(
        """
        INSERT INTO marks (evaluation_id, question_id, awarded_marks, comment, updated_at)
        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(evaluation_id, question_id) DO UPDATE SET
          awarded_marks = excluded.awarded_marks,
          comment = excluded.comment,
          updated_at = CURRENT_TIMESTAMP
        """,
        (evaluation_id, question["id"], awarded, str(mark.get("comment", ""))),
    )


def total_awarded(db: sqlite3.Connection, evaluation_id: int) -> float:
    row = db.execute(
        "SELECT COALESCE(SUM(awarded_marks), 0) AS total FROM marks WHERE evaluation_id = ?",
        (evaluation_id,),
    ).fetchone()
    return float(row["total"])


def submit_script(script_id: int) -> dict | None:
    with connect() as db:
        script = find_script(db, script_id)
        if script is None:
            return None

        evaluation = ensure_evaluation(db, script_id)
        db.execute(
            """
            UPDATE evaluations
            SET status = 'submitted', submitted_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (evaluation["id"],),
        )
        db.execute(
            """
            UPDATE answer_scripts
            SET status = 'submitted', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (script_id,),
        )
        write_audit_event(db, script_id, "submitted")
        db.commit()

    return get_script(script_id)


def write_audit_event(
    db: sqlite3.Connection,
    script_id: int,
    action: str,
    details: dict | None = None,
) -> None:
    db.execute(
        """
        INSERT INTO audit_events (actor_id, entity_type, entity_id, action, details)
        VALUES (?, 'answer_script', ?, ?, ?)
        """,
        (demo_evaluator_id(db), script_id, action, json.dumps(details or {})),
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "OSMMockAPI/0.2"

    def do_GET(self) -> None:
        path = clean_path(self.path)

        if path == ["health"]:
            self.send_json({"status": "ok"})
            return

        if path == ["api", "scripts"]:
            self.send_json({"scripts": list_scripts()})
            return

        if len(path) == 3 and path[:2] == ["api", "scripts"]:
            self.send_script(path[2])
            return

        self.send_error_json(HTTPStatus.NOT_FOUND, "Route not found")

    def do_PATCH(self) -> None:
        path = clean_path(self.path)

        is_marks_route = len(path) == 4 and path[:2] == ["api", "scripts"] and path[3] == "marks"
        if is_marks_route:
            script_id = parse_int(path[2])
            if script_id is None:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Script not found")
                return

            try:
                body = self.read_json_body()
                script = save_marks(
                    script_id,
                    body.get("marks", []),
                    body.get("remarks", ""),
                )
            except (json.JSONDecodeError, ValueError) as error:
                self.send_error_json(HTTPStatus.BAD_REQUEST, str(error))
                return

            if script is None:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Script not found")
                return

            self.send_json(script)
            return

        self.send_error_json(HTTPStatus.NOT_FOUND, "Route not found")

    def do_POST(self) -> None:
        path = clean_path(self.path)

        is_submit_route = len(path) == 4 and path[:2] == ["api", "scripts"] and path[3] == "submit"
        if is_submit_route:
            script_id = parse_int(path[2])
            if script_id is None:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Script not found")
                return

            script = submit_script(script_id)
            if script is None:
                self.send_error_json(HTTPStatus.NOT_FOUND, "Script not found")
                return

            self.send_json(script)
            return

        self.send_error_json(HTTPStatus.NOT_FOUND, "Route not found")

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.send_cors_headers()
        self.end_headers()

    def send_script(self, script_id_value: str) -> None:
        script_id = parse_int(script_id_value)
        if script_id is None:
            self.send_error_json(HTTPStatus.NOT_FOUND, "Script not found")
            return

        script = get_script(script_id)
        if script is None:
            self.send_error_json(HTTPStatus.NOT_FOUND, "Script not found")
            return

        self.send_json(script)

    def read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length == 0:
            return {}

        return json.loads(self.rfile.read(length).decode("utf-8"))

    def send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status: HTTPStatus, message: str) -> None:
        self.send_json({"error": message}, status)

    def send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PATCH, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")


def clean_path(raw_path: str) -> list[str]:
    return [part for part in urlparse(raw_path).path.split("/") if part]


def parse_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def main() -> None:
    initialize_database()
    address = (API_HOST, API_PORT)
    print(f"OSM mock API running at http://{API_HOST}:{API_PORT}")
    ThreadingHTTPServer(address, Handler).serve_forever()


if __name__ == "__main__":
    main()
