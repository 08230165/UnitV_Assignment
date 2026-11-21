
import sqlite3
from contextlib import closing
from datetime import datetime
from pathlib import Path


# Database location
DB_PATH = Path(__file__).resolve().parent / "tasks.db"


def get_connection():
    """Connect to the SQLite database."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the tasks table if it does not exist."""

    with closing(get_connection()) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    priority TEXT NOT NULL
                        CHECK(priority IN ('Low', 'Medium', 'High')),
                    due_date TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0
                        CHECK(completed IN (0, 1)),
                    created_at TEXT NOT NULL
                )
            """)


def validate_task(title, description, priority, due_date):
    """Validate information entered by the user."""

    title = title.strip()
    description = description.strip()

    if not title:
        raise ValueError("Please enter a task title.")

    if len(title) > 100:
        raise ValueError(
            "Task title cannot exceed 100 characters."
        )

    if priority not in ("Low", "Medium", "High"):
        raise ValueError("Please select a valid priority.")

    try:
        parsed_date = datetime.strptime(
            due_date, "%Y-%m-%d"
        )

        if parsed_date.strftime("%Y-%m-%d") != due_date:
            raise ValueError

    except ValueError:
        raise ValueError("Please select a valid due date.")

    return title, description, priority, due_date


def add_task(title, description, priority, due_date):
    """Save a new task."""

    title, description, priority, due_date = validate_task(
        title, description, priority, due_date
    )

    created_at = datetime.now().isoformat(
        timespec="seconds"
    )

    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute("""
                INSERT INTO tasks (
                    title,
                    description,
                    priority,
                    due_date,
                    completed,
                    created_at
                )
                VALUES (?, ?, ?, ?, 0, ?)
            """, (
                title,
                description,
                priority,
                due_date,
                created_at
            ))

            return cursor.lastrowid


def get_all_tasks():
    """Retrieve all tasks ordered by status and due date."""

    with closing(get_connection()) as connection:
        cursor = connection.execute("""
            SELECT *
            FROM tasks
            ORDER BY completed ASC, due_date ASC, id DESC
        """)

        return [dict(row) for row in cursor.fetchall()]


def get_task_by_id(task_id):
    """Retrieve one task using its ID."""

    with closing(get_connection()) as connection:
        cursor = connection.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )

        row = cursor.fetchone()

        if row:
            return dict(row)

        return None


def update_task(task_id, title, description, priority, due_date):
    """Update an existing task."""

    title, description, priority, due_date = validate_task(
        title, description, priority, due_date
    )

    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute("""
                UPDATE tasks
                SET title = ?,
                    description = ?,
                    priority = ?,
                    due_date = ?
                WHERE id = ?
            """, (
                title,
                description,
                priority,
                due_date,
                task_id
            ))

            return cursor.rowcount > 0


def delete_task(task_id):
    """Delete a task from the database."""

    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,)
            )

            return cursor.rowcount > 0


def set_task_completed(task_id, completed):
    """Mark a task as completed or pending."""

    if completed not in (0, 1):
        raise ValueError("Invalid completion status.")

    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute("""
                UPDATE tasks
                SET completed = ?
                WHERE id = ?
            """, (completed, task_id))

            return cursor.rowcount > 0


def get_task_counts():
    """Calculate task statistics."""

    with closing(get_connection()) as connection:
        cursor = connection.execute("""
            SELECT
                COUNT(*) AS total,

                COALESCE(
                    SUM(completed), 0
                ) AS completed,

                COALESCE(
                    SUM(
                        CASE
                            WHEN completed = 0 THEN 1
                            ELSE 0
                        END
                    ), 0
                ) AS pending

            FROM tasks
        """)

        return dict(cursor.fetchone())
