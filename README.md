# TaskFlow – Smart Task Manager

**Unit V Assignment: Exploring GUI Frameworks (PyQt, Kivy & Alternatives)**  
**Student:** Pema Cheki  
**Roll Number:** 14  
**Project type:** Python desktop GUI application  
**Main framework:** PyQt6  
**Database:** SQLite

## 1. Project Overview

TaskFlow is a desktop to-do and task management application developed with Python, PyQt6 and SQLite. It helps users organize assignments and everyday tasks, set priorities and deadlines, monitor progress, and manage completed work. Tasks are stored locally in an SQLite database, so information remains available after the application is closed and reopened.

This submission also includes three small **Part A** programs demonstrating a greeting button in Tkinter, Kivy and PyQt6.

## 2. Main Features

| Page | Features |
| --- | --- |
| **Dashboard** | Total, pending, completed and overdue task counts; completion progress; priority chart; upcoming tasks |
| **My Tasks** | Add, edit, delete, complete and reopen tasks; title, optional description, priority and due date; search, filter and sort |
| **Calendar** | Browse tasks for a whole month, select a specific date, return to the monthly task list, and create a task with the selected due date |
| **Completed Tasks** | View completed tasks and mark selected tasks as pending again |

Additional features include user-friendly validation, delete confirmation, a date-picker popup, coloured task priorities, overdue highlighting, and a custom application theme.

## 3. System Requirements

- Python **3.10 or later** (the student's current development environment uses Python 3.12 on Windows).
- A graphical desktop environment; Windows is the primary development environment.
- PyQt6 and Kivy, installed using `requirements.txt`.
- Tkinter, normally included with standard Python installations on Windows.
- `pip` and an internet connection for initial package installation.

SQLite is part of Python's standard library; no separate database server is required.

## 4. Project Structure

```text
14_PemaCheki_UnitV/
├── part A/
│   ├── tkinter_hello.py       # Tkinter greeting demonstration
│   ├── kivy_hello.py          # Kivy greeting demonstration
│   └── pyqt_hello.py          # PyQt6 greeting demonstration
├── part B/
│   ├── main.py                # TaskFlow user interface and events
│   ├── database.py            # SQLite operations and validation
│   ├── tasks.db               # Sample task database
│   ├── test_taskflow.py       # Automated database tests
│   └── requirements.txt       # Pinned dependencies
└── README.md                  # Setup and usage guide
```

The `.venv` directory is created locally during setup and **should not** be included in the submission ZIP. The submission preparation script, if used, can remain outside the ZIP.

## 5. Installation – Windows (PowerShell)

1. Extract `14_PemaCheki_UnitV.zip` to a convenient folder.
2. Open the extracted `14_PemaCheki_UnitV` folder in VS Code.
3. Open **Terminal → New Terminal** in VS Code. Make sure the terminal is in the project root (the folder containing `part A` and `part B`).
4. Create a virtual environment:

```powershell
python -m venv .venv
```

5. Install the required packages using the virtual environment's Python:

```powershell
.\.venv\Scripts\python.exe -m pip install -r "part B/requirements.txt"
```

**Note:** The folders are named `part A` and `part B` **with spaces**. Keep quotation marks around paths in commands. Using `.venv\Scripts\python.exe` directly avoids PowerShell activation-policy problems and ensures that packages are installed into the correct environment.

## 6. Run the Main Application

From the project root, execute:

```powershell
.\.venv\Scripts\python.exe "part B/main.py"
```

The TaskFlow desktop window opens. Use the sidebar to navigate between **Dashboard**, **My Tasks**, **Calendar**, and **Completed Tasks**.

## 7. How to Use TaskFlow

### Add a Task

1. Select **My Tasks** from the sidebar.
2. Enter a task title (required) and, optionally, a description.
3. Choose **Low**, **Medium**, or **High** priority.
4. Choose a due date using the date field or **Choose Date** calendar popup.
5. Click **Add Task**. The task is saved and appears in the table.

### Edit, Complete, or Delete

- **Edit:** Select a row, click **Edit Task**, change the details, and click **Save Changes**. Use **Cancel Editing** to discard the edits.
- **Complete / Reopen:** Select a row and use **Mark Completed** or **Mark Pending**.
- **Delete:** Select a row, click **Delete Task**, and confirm the deletion. This action is permanent.
- **Find Tasks:** Use the search field, priority/status filters, sorting options, and **Clear Filters**.

### Use the Calendar

1. Open **Calendar** to view tasks due in the displayed month.
2. Change the month using the calendar's navigation controls.
3. Click a date to view tasks due on that day.
4. Click **Show All Month Tasks** to return to the monthly overview.
5. Click **Create Task for Selected Date** to open the task form with that date preselected.

### View Completed Tasks

Open **Completed Tasks** to see finished work. Select a completed task and use the button to mark it pending again.

## 8. Run the Part A GUI Demonstrations

Open each application separately from the project root:

```powershell
.\.venv\Scripts\python.exe "part A/tkinter_hello.py"
.\.venv\Scripts\python.exe "part A/kivy_hello.py"
.\.venv\Scripts\python.exe "part A/pyqt_hello.py"
```

Each demonstration displays a greeting interface and changes its displayed message when **Say Hello** is clicked. Close one application before launching the next.

## 9. Database and Data Persistence

`part B/tasks.db` is the SQLite database. The database is opened using a path relative to `database.py`, rather than a hard-coded absolute path. Task data is preserved when TaskFlow closes.

If `tasks.db` is missing, the application creates a new empty database when launched. **Keep the included `tasks.db` if you want to retain the sample tasks.** Do not delete the database during normal use.

## 10. Testing

### Automated Database Tests

Run:

```powershell
.\.venv\Scripts\python.exe "part B/test_taskflow.py"
```

**Recorded test result:** The student ran 14 tests and reported the terminal result `OK`. The tests cover database operations, input validation and data persistence. They use a temporary test database and do not modify the real `tasks.db`.

### Manual GUI Tests

Manually check that task creation, editing, completion, deletion confirmation, search and filters, monthly calendar navigation, completed-task reopening, and the dashboard work as expected. Record actual observed results and screenshots in the final report; automated database tests alone do not validate the full GUI.

## 11. Troubleshooting

| Problem | What to check |
| --- | --- |
| `can't open file ... partB/main.py` | Use the actual directory name, `"part B/main.py"`, with a space. |
| `No module named PyQt6` | Install dependencies using `.\.venv\Scripts\python.exe -m pip install -r "part B/requirements.txt"`. |
| `No module named PyQt6.sip` | Reinstall dependencies inside the same `.venv`. Verify the interpreter is the virtual environment's Python. |
| `cannot import name ... from database` | Ensure `main.py` and `database.py` are the matching latest versions in the same `part B` folder. |
| Tasks disappear after reopening | Check that the same `part B/tasks.db` is being used and that the file has not been deleted or replaced. |
| Input fields or text are clipped | Maximize the window, use the application scroll area, and check Windows display scaling. |



## 12. Technologies and References

- Python: https://www.python.org/
- PyQt6 documentation: https://www.riverbankcomputing.com/static/Docs/PyQt6/
- Kivy documentation: https://kivy.org/doc/stable/
- Tkinter documentation: https://docs.python.org/3/library/tkinter.html
- SQLite documentation: https://docs.python.org/3/library/sqlite3.html

---

**Prepared by:** Pema Cheki · **Roll No.:** 14  
**Application:** TaskFlow – Smart Task Manager
