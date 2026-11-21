"""Automated SQLite tests for TaskFlow (does not modify the real tasks.db)."""
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# This test file belongs inside the same 'part B' folder as database.py.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import database


class TestTaskFlowDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_file = Path(self.temp_dir.name) / "test_tasks.db"
        self.path_patch = patch.object(database, "DB_PATH", self.db_file)
        self.path_patch.start()
        database.initialize_database()

    def tearDown(self):
        self.path_patch.stop()
        self.temp_dir.cleanup()

    def new_task(self, title="Assignment 1", priority="High", due="2026-11-20"):
        return database.add_task(title, "Finish GUI coursework", priority, due)

    def test_01_database_created(self):
        self.assertTrue(self.db_file.exists())

    def test_02_add_task(self):
        task_id = self.new_task()
        task = database.get_task_by_id(task_id)
        self.assertEqual(task["title"], "Assignment 1")
        self.assertEqual(task["priority"], "High")
        self.assertEqual(task["due_date"], "2026-11-20")

    def test_03_empty_title_rejected(self):
        with self.assertRaises(ValueError):
            database.add_task("   ", "Description", "Medium", "2026-11-20")

    def test_04_long_title_rejected(self):
        with self.assertRaises(ValueError):
            database.add_task("A" * 101, "", "Medium", "2026-11-20")

    def test_05_invalid_priority_rejected(self):
        with self.assertRaises(ValueError):
            database.add_task("Study", "", "Urgent", "2026-11-20")

    def test_06_invalid_date_rejected(self):
        with self.assertRaises(ValueError):
            database.add_task("Study", "", "Low", "2026-02-30")

    def test_07_edit_task(self):
        task_id = self.new_task()
        changed = database.update_task(task_id, "Assignment 1 Updated", "Edited", "Low", "2026-11-25")
        self.assertTrue(changed)
        task = database.get_task_by_id(task_id)
        self.assertEqual(task["title"], "Assignment 1 Updated")
        self.assertEqual(task["priority"], "Low")

    def test_08_mark_completed(self):
        task_id = self.new_task()
        self.assertTrue(database.set_task_completed(task_id, 1))
        self.assertEqual(database.get_task_by_id(task_id)["completed"], 1)

    def test_09_reopen_pending(self):
        task_id = self.new_task()
        database.set_task_completed(task_id, 1)
        self.assertTrue(database.set_task_completed(task_id, 0))
        self.assertEqual(database.get_task_by_id(task_id)["completed"], 0)

    def test_10_delete_task(self):
        task_id = self.new_task()
        self.assertTrue(database.delete_task(task_id))
        self.assertIsNone(database.get_task_by_id(task_id))

    def test_11_dashboard_counts(self):
        first = self.new_task("Task A")
        self.new_task("Task B", "Medium")
        database.set_task_completed(first, 1)
        counts = database.get_task_counts()
        self.assertEqual(counts["total"], 2)
        self.assertEqual(counts["completed"], 1)
        self.assertEqual(counts["pending"], 1)

    def test_12_persistence_between_connections(self):
        task_id = self.new_task()
        # get_task_by_id opens a new SQLite connection, simulating a reopen.
        self.assertEqual(database.get_task_by_id(task_id)["title"], "Assignment 1")

    def test_13_ordered_tasks(self):
        self.new_task("Later", "Low", "2026-11-29")
        self.new_task("Earlier", "High", "2026-11-18")
        tasks = database.get_all_tasks()
        self.assertEqual([t["title"] for t in tasks], ["Earlier", "Later"])

    def test_14_missing_task_handled(self):
        self.assertIsNone(database.get_task_by_id(999999))
        self.assertFalse(database.delete_task(999999))
        self.assertFalse(database.update_task(999999, "Valid", "", "Low", "2026-11-20"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
