# 📘 Pytest — Ultra Detailed Explanation (For Complete Beginners)
## Every Single Line Explained Like You Are 10 Years Old

---

# 🗂️ OVERVIEW — What Files Did We Create/Change?

```
CREATED (brand new files):
  pytest.ini                           ← tells pytest HOW to behave
  webapp/tests/__init__.py             ← makes the tests folder a Python package
  webapp/tests/conftest.py             ← shared fixtures + custom HTML report generator
  webapp/tests/test_login_view.py      ← 15 actual tests for the login page
  test-results/custom_report.html      ← modern dark-theme HTML report (auto-generated)
  test-results/test.log                ← plain text log of Django logging during tests

MODIFIED (changed existing files):
  webapp/urls.py                       ← added name= to every URL pattern
  webapp/forms.py                      ← fixed a real hidden bug discovered by tests
  requirements.txt                     ← added pytest, pytest-django packages

REFERENCE DOCUMENTS (in deploy/09-TESTING/):
  HOW_TO_RUN_TESTS.md                  ← every command to run tests, with examples
  PYTEST_FIXTURES_REFERENCE.md         ← all built-in fixtures listed with examples
  PYTEST_VS_PYTEST_DJANGO.md           ← difference between pytest and pytest-django
```

---

# 🧠 BEFORE WE START — What Even Is pytest?

Imagine you bake a cake. After baking, you taste it to check:
- Does it taste right? ✅
- Is it fully cooked? ✅
- Did it rise properly? ✅

That "tasting and checking" = **testing**.

**pytest** is a tool that does this tasting **automatically** for your Python/Django code.

Instead of you manually opening the browser, clicking Login, typing wrong passwords,
and checking if an error message appears — you write a test once, and pytest
does all the clicking and checking for you, every single time, in seconds.

---

# 📄 FILE 1 — `pytest.ini`

**Location:** `D:\webProject\pytest.ini`
**What it is:** A settings/configuration file for pytest.
Think of it like the `settings.py` for your Django project — but this one is for pytest.

When you type `pytest` in the terminal, pytest reads this file FIRST to understand:
- Which Django settings to use
- Which files are test files
- How to display results

---

## Full File:

```ini
[pytest]
# DJANGO_SETTINGS_MODULE: tells pytest which Django settings file to use
DJANGO_SETTINGS_MODULE = webProject.settings
# python_files: only scan files whose name starts with test_
python_files = test_*.py
# python_classes: only treat classes starting with Test as test groups
python_classes = Test*
# python_functions: only treat functions starting with test_ as actual tests
python_functions = test_*
# addopts: verbose + short tracebacks on failure + modern report auto-generated via conftest hook
addopts = -v
          --tb=short
# log_cli: show log output in the console while tests run
log_cli = true
log_cli_level = INFO
# log_file: also write all log output to a plain text file
log_file = test-results/test.log
log_file_level = INFO
log_file_format = %(asctime)s [%(levelname)s] %(message)s
log_file_date_format = %Y-%m-%d %H:%M:%S
```

---

## Line by Line:

### Line 1: `[pytest]`
```ini
[pytest]
```
This is like a label/header.
It says "everything below this line is a setting for pytest".
This is standard `.ini` file syntax — just a way of organising settings.

---

### Line 2: `DJANGO_SETTINGS_MODULE = webProject.settings`
```ini
DJANGO_SETTINGS_MODULE = webProject.settings
```
**This is the most important line in the entire file.**

When pytest runs your tests, it needs to start Django first.
Django needs to know WHERE your settings file is.

`webProject.settings` means:
- Look inside the `webProject/` folder
- Find `settings.py`
- Load it

Without this line:
- Django does not know your database
- Django does not know your installed apps
- Django does not know your URL patterns
- NOTHING works — every test crashes immediately

With this line:
- pytest loads Django properly
- Your models work
- Your views work
- Everything works just like a normal Django request

---

### Line 3: `python_files = test_*.py`
```ini
python_files = test_*.py
```
**Tells pytest: "Only look for tests inside files whose name starts with `test_`"**

The `*` is a wildcard — it means "anything".
So `test_*.py` means:
- `test_login_view.py` ✅ (starts with test_)
- `test_signup.py`     ✅ (starts with test_)
- `views.py`           ❌ (does not start with test_)
- `forms.py`           ❌ (does not start with test_)

Why? Because your project has many `.py` files. pytest should not scan ALL of them.
Only files named `test_something.py` contain tests.

---

### Line 4: `python_classes = Test*`
```ini
python_classes = Test*
```
**Tells pytest: "Only treat classes starting with `Test` as test classes"**

Inside test files, we group tests using Python classes:
- `class TestLoginGET:`  ✅ (starts with Test)
- `class TestLoginPOST:` ✅ (starts with Test)
- `class LoginForm:`     ❌ (does not start with Test — not a test class)

This prevents pytest from accidentally treating your real Django classes as test classes.

---

### Line 5: `python_functions = test_*`
```ini
python_functions = test_*
```
**Tells pytest: "Only treat functions starting with `test_` as actual tests"**

Inside test classes, we have many functions:
- `def test_login_page_loads`      ✅ (starts with test_)
- `def test_empty_form_submission`  ✅ (starts with test_)
- `def helper_setup`               ❌ (does not start with test_ — it is a helper, not a test)

So you can have helper functions inside test files — pytest will not try to run them as tests.

---

### Line 6: `addopts = -v` + `--tb=short`
```ini
addopts = -v
          --tb=short
```
`addopts` = "additional options" — options to always add when running pytest.
`-v` = "verbose" — show detailed output.

**Without `-v` (boring output):**
```
......F...   (dots = passed, F = failed)
```

**With `-v` (helpful output):**
```
PASSED test_login_view.py::TestLoginGET::test_login_page_loads
PASSED test_login_view.py::TestLoginGET::test_login_page_uses_correct_template
FAILED test_login_view.py::TestLoginPOST::test_successful_login_redirects_to_home
```

`--tb=short` = "traceback short" — when a test FAILS, show a shorter error message.

**Without `--tb=short` (long — shows entire stack trace):**
```
FAILED test_login_view.py::TestLoginPOST::test_successful_login_redirects_to_home
  File "D:\webProject\webapp\views.py", line 45, in loginForm_view
    ...many lines of internal Django code...
  AssertionError: assert 200 == 302
```

**With `--tb=short` (shorter — just shows what matters):**
```
FAILED test_login_view.py::TestLoginPOST::test_successful_login_redirects_to_home
  AssertionError: assert 200 == 302
```

Much easier to read when learning. You see exactly WHAT failed, not the whole history of every function call.

---

### Lines 7–10: `log_cli` and `log_file`
```ini
log_cli = true
log_cli_level = INFO
log_file = test-results/test.log
log_file_level = INFO
log_file_format = %(asctime)s [%(levelname)s] %(message)s
log_file_date_format = %Y-%m-%d %H:%M:%S
```

These lines set up **logging** — capturing messages that your Django views write during tests.

**`log_cli = true`**
`cli` = command line interface (the terminal).
`true` = show log messages IN the terminal while tests run.
If your view has `logger.info("User logged in successfully")`, that message appears in the console.

**`log_cli_level = INFO`**
Only show log messages at INFO level or above.
Log levels from lowest to highest: DEBUG → INFO → WARNING → ERROR → CRITICAL.
Setting INFO means: show INFO, WARNING, ERROR, CRITICAL — but hide DEBUG (too noisy).

**`log_file = test-results/test.log`**
ALSO write all log messages to this plain text file.
After every test run, open `test-results/test.log` in any text editor.
You can review what your views logged during the tests.

**`log_file_format = %(asctime)s [%(levelname)s] %(message)s`**
How each log line is formatted:
```
2026-02-25 11:00:00 [INFO] User testuser logged in successfully
     ↑ time              ↑ level    ↑ the actual message
```

**Note:** `test.log` is empty if your views do not call `logger.info(...)` etc.
It fills up as you add more views that use Django's logging system.

---

### The Modern HTML Report — auto-generated by conftest.py hook
The old `--html=report.html` flag (from pytest-html plugin) has been **removed**.
Instead, `conftest.py` now contains a custom hook that generates a beautiful modern report.

Every time you run `pytest`, this file is auto-created:
```
test-results/custom_report.html
```

Open it in any browser. No plugin needed — it is pure HTML/CSS/JavaScript.

---

# 📄 FILE 2 — `webapp/tests/__init__.py`

**Location:** `D:\webProject\webapp\tests\__init__.py`
**What it is:** A completely empty file. Zero bytes. Not even a comment.

---

## Why does an empty file matter?

Python has a concept called **packages**.

A **package** = a folder that Python can `import` things from.

For Python to treat a folder as a package, that folder MUST contain `__init__.py`.

**Without `__init__.py`:**
```
webapp/
  tests/
    conftest.py           ← Python says: "I do not know how to import this"
    test_login_view.py    ← Python says: "I do not know how to import this"
```
pytest tries to import your test files. Python cannot do it. Tests crash.

**With `__init__.py`:**
```
webapp/
  tests/
    __init__.py           ← "✅ This folder is now a Python package"
    conftest.py           ← Python can now import this properly
    test_login_view.py    ← Python can now import this properly
```

Think of it like:
- A folder is just a box on your shelf
- `__init__.py` is the label on the box that says "this is a Python package"
- Without the label, Python ignores it

---

# 📄 FILE 3 — `webapp/tests/conftest.py`

**Location:** `D:\webProject\webapp\tests\conftest.py`

---

## What is conftest.py?

`conftest.py` is a **special magic file** that pytest automatically finds and loads
BEFORE running any test.

You never import it. You never call it. pytest finds it automatically.

Any **fixture** (explained below) defined in conftest.py is available to
EVERY test file in the same folder — without any import statement.

**Real world analogy:**
Imagine an office kitchen.
The conftest.py is the shared kitchen — coffee machine, cups, spoons — available to everyone.
Instead of every employee bringing their own coffee machine, they all use the shared one.

---

## ⚡ NEW — conftest.py now has THREE responsibilities:

```
1. _results list         ← collects test results as each test finishes
2. Hook 1 (per-test)     ← called after every test, stores result in _results
3. Hook 2 (at the end)   ← called once after ALL tests, generates the HTML report
4. Fixtures              ← test_user, admin_user, logged_in_client (same as before)
```

---

## ❓ What Is a Fixture? (Most Important Concept in pytest)

A **fixture** is a function that **prepares something** for your tests.

Before each test, you might need:
- A user in the database
- A logged-in browser session
- A specific piece of data

Instead of writing that setup code inside EVERY test (copy-pasting),
you write it ONCE as a fixture. Tests just ask for it by name.

**WITHOUT fixtures (bad — lots of repetition):**
```python
def test_something(client):
    # Create a user first (copying this into every single test!)
    user = User.objects.create_user(username='testuser', password='Pass123!')
    client.force_login(user)
    response = client.get('/home/')
    assert response.status_code == 200

def test_something_else(client):
    # Same user creation code copied again :(
    user = User.objects.create_user(username='testuser', password='Pass123!')
    client.force_login(user)
    response = client.get('/audio/')
    assert response.status_code == 200
```

**WITH fixtures (good — clean and reusable):**
```python
# Define ONCE in conftest.py
@pytest.fixture
def logged_in_client(client, test_user):
    client.force_login(test_user)
    return client

# Use in ANY test — just add the name as a parameter
def test_something(logged_in_client):
    response = logged_in_client.get('/home/')
    assert response.status_code == 200

def test_something_else(logged_in_client):
    response = logged_in_client.get('/audio/')
    assert response.status_code == 200
```

pytest sees `logged_in_client` as a parameter → automatically runs the fixture → passes the result in.
**You never call the fixture manually.** pytest does it for you.

---

## 🪝 What Is a Hook?

A **hook** is a function that pytest calls automatically at specific moments.

| Hook name | When it runs |
|---|---|
| `pytest_runtest_makereport` | After EVERY single test |
| `pytest_sessionfinish` | Once after ALL tests finish |
| `pytest_configure` | When pytest first starts up |
| `pytest_collection_finish` | After all tests are collected |

We use two hooks in conftest.py:
- `pytest_runtest_makereport` — grabs each test result as it happens
- `pytest_sessionfinish` — builds the HTML report from all collected results

---

## Full File Explained — Part 1: Imports and _results List

```python
import pytest
import os
import json
import datetime
from django.contrib.auth.models import User

_results = []
```

### `import pytest`
Loads the pytest library for `@pytest.fixture`, `@pytest.hookimpl`, etc.

### `import os`
Python's built-in module for file and folder operations.
We use `os.makedirs('test-results', exist_ok=True)` to create the output folder.

### `import json`
Python's built-in module for converting Python data to JSON format.
We use it to build the chart data for the HTML report:
```python
json.dumps(['TestLoginGET', 'TestLoginPOST'])  →  '["TestLoginGET", "TestLoginPOST"]'
```
Chart.js (the JavaScript charting library) needs data in JSON format.

### `import datetime`
Python's built-in module for dates and times.
Used to put the current date/time on the report:
```python
datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')
→  'February 25, 2026 at 11:00 PM'
```

### `_results = []`
A **module-level list** — it lives for the entire duration of the pytest session.
Every time a test finishes, Hook 1 appends a dictionary to this list.
By the time all tests finish, `_results` contains one entry per test.

The `_` prefix by Python convention means "internal — not meant to be used outside this file".

```python
# After 3 tests run, _results looks like:
_results = [
    {'module': 'test_login_view.py', 'cls': 'TestLoginGET', 'fn': 'test_login_page_loads',    'status': 'passed', 'duration': 0.123, 'longrepr': ''},
    {'module': 'test_login_view.py', 'cls': 'TestLoginGET', 'fn': 'test_login_page_has_form',  'status': 'passed', 'duration': 0.089, 'longrepr': ''},
    {'module': 'test_login_view.py', 'cls': 'TestLoginPOST','fn': 'test_empty_form_submission', 'status': 'failed', 'duration': 0.201, 'longrepr': 'AssertionError: assert 200 == 302'},
]
```

---

## Full File Explained — Part 2: Hook 1 (pytest_runtest_makereport)

```python
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == 'call':
        parts  = item.nodeid.replace('\\', '/').split('::')
        module = parts[0].replace('webapp/tests/', '')
        cls    = parts[1] if len(parts) > 2 else '-'
        fn     = parts[-1]
        _results.append({
            'module':   module,
            'cls':      cls,
            'fn':       fn,
            'status':   'passed' if rep.passed else ('failed' if rep.failed else 'skipped'),
            'duration': round(rep.duration, 3),
            'longrepr': str(rep.longrepr) if rep.failed else '',
        })
```

### `@pytest.hookimpl(tryfirst=True, hookwrapper=True)`

This is a **decorator** that tells pytest: "register this function as a hook implementation".

`tryfirst=True` = run this hook BEFORE any other plugin hooks. Ensures we get the result first.

`hookwrapper=True` = this hook WRAPS around the normal pytest process.
It pauses (`yield`) to let pytest do its work, then resumes to read the result.

Think of it like:
```
Our code BEFORE  →  yield (pytest does the test)  →  Our code AFTER
```

### `def pytest_runtest_makereport(item, call):`

The function name MUST be exactly `pytest_runtest_makereport` — that is how pytest finds it.

`item` = the test item (contains `item.nodeid` like `webapp/tests/test_login_view.py::TestLoginGET::test_login_page_loads`)
`call` = which phase is being reported (setup, call, or teardown)

### `outcome = yield`

`yield` pauses our hook and lets pytest run the actual test.
After the test finishes, `yield` returns and we get the result back.

`outcome` = the result of pytest running the test.

### `rep = outcome.get_result()`

Gets the actual report object from the outcome.
`rep` has these properties:
- `rep.when` → which phase: `'setup'`, `'call'`, or `'teardown'`
- `rep.passed` → True if the test passed
- `rep.failed` → True if the test failed
- `rep.skipped` → True if the test was skipped
- `rep.duration` → how many seconds the test took
- `rep.longrepr` → the full error traceback if failed (empty if passed)

### `if rep.when == 'call':`

A test has 3 phases: setup → call → teardown.
We only care about `'call'` — that is when the actual test body ran.
Without this check, we would store 3 entries per test (setup + call + teardown).

### `item.nodeid.replace('\\', '/').split('::')`

`item.nodeid` looks like:
```
webapp\tests\test_login_view.py::TestLoginGET::test_login_page_loads
```

`.replace('\\', '/')` → normalises Windows backslashes to forward slashes:
```
webapp/tests/test_login_view.py::TestLoginGET::test_login_page_loads
```

`.split('::')` → splits on `::` to get individual parts:
```python
['webapp/tests/test_login_view.py', 'TestLoginGET', 'test_login_page_loads']
#        parts[0]                      parts[1]              parts[2]
```

### `module = parts[0].replace('webapp/tests/', '')`

Removes the folder prefix to just get the filename:
```
webapp/tests/test_login_view.py  →  test_login_view.py
```

### `cls = parts[1] if len(parts) > 2 else '-'`

`len(parts) > 2` checks if there IS a class name in the nodeid.
If the test is not inside a class, `parts` only has 2 elements (file + function).
In that case we use `'-'` as a placeholder.

### `fn = parts[-1]`

`parts[-1]` = the LAST item in the list = the function name.
`-1` in Python means "count from the end": `[-1]` is last, `[-2]` is second-to-last.

### `_results.append({...})`

Adds a dictionary with all the test data to the `_results` list.
Every test that finishes adds its data here.
`'longrepr'` = the error message (only populated if the test failed).

---

## Full File Explained — Part 3: Hook 2 (pytest_sessionfinish)

```python
def pytest_sessionfinish(session, exitstatus):
    os.makedirs('test-results', exist_ok=True)
    ...
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
```

### `def pytest_sessionfinish(session, exitstatus):`

Called ONCE after ALL tests have finished.

`session` = the pytest session object (contains info about the whole run)
`exitstatus` = 0 if all tests passed, non-zero if any failed

### `os.makedirs('test-results', exist_ok=True)`

Creates the `test-results/` folder if it does not already exist.
`exist_ok=True` = do NOT raise an error if the folder already exists.
Without `exist_ok=True`, if `test-results/` already exists, this line crashes.

### What the function builds:

It calculates totals from `_results`:
```python
n_passed = sum(1 for r in _results if r['status'] == 'passed')
n_failed = sum(1 for r in _results if r['status'] == 'failed')
pass_pct = round((n_passed / total * 100), 1)
```

Then it builds:
- **HTML table rows** — one `<tr>` per test, colour-coded
- **Chart.js doughnut data** — `[15, 0, 0]` for 15 passed, 0 failed, 0 skipped
- **Chart.js bar data** — grouped by class name
- **Full HTML string** — the complete self-contained page

Finally writes it to `test-results/custom_report.html`.

---

## The custom_report.html — What It Contains

Every time you run `pytest`, `test-results/custom_report.html` is auto-generated.
Open it in any browser — right-click the file in PyCharm → Open In → Browser.

**What you see in the report:**

```
🧪 Test Report                                   📅 February 25, 2026 at 11:00 PM
webProject — Django Test Suite                   Python 3.12 · Django 5.2.8 · pytest 9.0.2

┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Total Tests │  │   Passed    │  │   Failed    │  │   Skipped   │  │  Pass Rate  │
│     15      │  │     15      │  │      0      │  │      0      │  │   100.0%    │
└─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘

[████████████████████████████████████████████] 100% passing

[Doughnut chart: green=15]    [Bar chart: one bar group per test class]

File               Class                  Test Name                          Status    Duration
test_login_view.py TestLoginGET           test_login_page_loads              PASSED    0.123s
test_login_view.py TestLoginGET           test_login_page_uses_correct_..    PASSED    0.089s
...
```

**Interactive features:**
- 🔍 Search box — type to filter tests instantly
- Click any FAILED row to expand the full error traceback
- Colour-coded rows — green hover for passed, red hover for failed

---

## Full File Explained — Part 4: Fixtures (unchanged)

```python
@pytest.fixture(scope='function')
def test_user(db):
```

### `@pytest.fixture`
This **decorator** transforms `test_user` from a normal function into a pytest fixture.
Without `@pytest.fixture`, pytest would try to run it as a test and fail.
With `@pytest.fixture`, pytest knows: "this is setup code for other tests to use".

### `def test_user(db):`
Defines the fixture function named `test_user`.

**The `db` parameter is itself a built-in pytest-django fixture.**

By default, pytest-django **blocks all database access** in tests.
Why? Because database operations are slow. If tests do not need the DB, blocking it makes them faster.

`db` is pytest-django's built-in fixture that **unlocks database access**.
By putting `db` as a parameter of `test_user`, our fixture gets database access.
And any test that uses `test_user` automatically inherits that database access.

**Chain of access:**
```
db (built-in)  →  test_user fixture  →  your test function
```
Like a permission chain — if you have the key (db), everyone you give the key to can open the door.

---

```python
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='StrongPass123!'
    )
```

### `User.objects.create_user(...)`
Creates a new User in the **test database** (not your real database — explained later).

`create_user` vs `create`:
- `User.objects.create(password='abc')` stores the password as plain text — **NEVER do this** (insecure)
- `User.objects.create_user(password='abc')` automatically **hashes** the password (secure)

Hashing = converting `StrongPass123!` → a scrambled string like `$argon2$...abc123...`
The scrambled version is what gets stored. Django can verify passwords without storing the original.

### `return user`
Returns the User object so tests can use it.
When a test does `def test_something(self, client, test_user):`,
the `test_user` parameter receives this returned User object.
So inside the test you can do `test_user.email`, `test_user.username`, etc.

---

```python
@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username='adminuser',
        email='admin@example.com',
        password='AdminPass123!'
    )
```

### `create_superuser` vs `create_user`

`create_user`:
- `is_staff = False` (cannot access Django admin panel)
- `is_superuser = False` (no special permissions)
- Regular user

`create_superuser`:
- `is_staff = True` (CAN access Django admin panel)
- `is_superuser = True` (has ALL permissions automatically)
- Admin user

**When to use `admin_user`:**
If you have views that only admins can access (decorated with `@staff_member_required`
or checking `request.user.is_staff`), you need an admin user to test them.

---

```python
@pytest.fixture
def logged_in_client(client, test_user):
    client.force_login(test_user)
    return client
```

### `client`
`client` is a **built-in pytest-django fixture** — a fake web browser.
It can:
- `client.get('/some/url/')` → simulate opening a URL in a browser
- `client.post('/some/url/', data={...})` → simulate submitting a form
- Check response status codes, content, cookies, session, etc.

It does NOT open a real browser. It makes HTTP requests directly to your Django views.
This is much faster than Selenium/real browser testing.

### `test_user`
Notice `test_user` is a PARAMETER of `logged_in_client`.
This means: "before running `logged_in_client`, first run the `test_user` fixture".
pytest automatically chains them: run `test_user` first → pass result into `logged_in_client`.

### `client.force_login(test_user)`
`force_login` = directly logs in the user, bypassing the entire login form.

**The difference:**
```
Normal login:  POST to /loginpage/ with email+password → form validates → authenticate() → login()
force_login:   Directly sets the session cookie as if user already logged in
```

`force_login` is for when you want to test a view that **requires** login,
but you are NOT testing the login process itself.


### `return client`
Returns the client that now has an active session (logged-in).
Any test that uses `logged_in_client` gets a fake browser that is already logged in.

---

## 🔁 Fixture Scope — How Long Does a Fixture Live?

Every fixture has a **scope** — how long it lives before being recreated.

```python
@pytest.fixture(scope='function')   # DEFAULT — recreated for each test
@pytest.fixture(scope='class')      # recreated once per class
@pytest.fixture(scope='module')     # recreated once per file
@pytest.fixture(scope='session')    # recreated once per entire test run
```

**Default is `scope='function'`** — each test gets a fresh copy.

**Example with scope='function' (default):**
```
test_login_page_loads     → fresh test_user created → test runs → user deleted
test_page_has_form        → fresh test_user created → test runs → user deleted
test_empty_submission     → fresh test_user created → test runs → user deleted
```

Why fresh each time? So tests do not affect each other.
If one test modifies the user and the next test expects the original user, you get false failures.
Fresh fixtures = isolated tests = reliable results.

---

# 📄 FILE 4 — `webapp/tests/test_login_view.py`

**Location:** `D:\webProject\webapp\tests\test_login_view.py`
**What it tests:** The login page (`loginForm_view` in `views.py`) at `/loginpage/`

---

## The Imports

```python
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
```

### `import pytest`
Loads pytest. Needed for `@pytest.fixture`, `@pytest.mark.parametrize`, etc.

### `from django.contrib.auth.models import User`
The User model — needed to create test users and check authentication.

### `from django.urls import reverse`
`reverse()` converts a URL **name** to an actual URL **path**.

Example:
```python
reverse('loginpage')   # returns '/loginpage/'
reverse('home')        # returns '/home/'
reverse('audio')       # returns '/audio/'
```

**Why use `reverse()` instead of typing `/loginpage/` directly?**

Imagine you change your URL from `/loginpage/` to `/login/` in `urls.py`.
- With hardcoded path: you must update EVERY test that uses `/loginpage/` — many places
- With `reverse('loginpage')`: you change it in `urls.py` once — ALL tests automatically work

`reverse()` is connected to the `name=` you give each URL in `urls.py`:
```python
# In urls.py:
path('loginpage/', views.loginForm_view, name='loginpage')
#                                         ↑ this is what reverse() looks up
```

---

## The Local `test_user` Fixture in This File

```python
@pytest.fixture
def test_user(db):
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='StrongPass123!'
    )
    return user
```

This is the same fixture as in `conftest.py`!
This file was written first as a learning example with the fixture defined locally.
Then we moved it to `conftest.py` so all test files can share it.
The local version here still works — when pytest finds a fixture in both the test file
AND `conftest.py`, the local one takes priority for tests in that file.

The line `user = ...` stores the created user object in a variable named `user`.
The line `return user` gives that object back to whoever asked for the fixture.

---

## GROUP 1 — `class TestLoginGET`

```python
class TestLoginGET:
```
A Python class used to **group related tests**.
All tests about GET requests to the login page live here.

Using classes helps you:
- Organise tests by behaviour
- Run just one group: `pytest test_login_view.py::TestLoginGET -v`
- Read the test file easily — it is structured, not a long flat list

The class name starts with `Test` because of `python_classes = Test*` in pytest.ini.

---

### Test 1: `test_login_page_loads`

```python
def test_login_page_loads(self, client):
    url = reverse('loginpage')
    response = client.get(url)
    assert response.status_code == 200
```

#### `def test_login_page_loads(self, client):`
`self` — standard Python — refers to the class instance.
`client` — pytest-django's fake browser fixture. Automatically injected by pytest.

#### `url = reverse('loginpage')`
`reverse('loginpage')` returns the string `'/loginpage/'`.
We store it in `url` so we can reuse it.

#### `response = client.get(url)`
Simulates: open a browser → type `http://localhost/loginpage/` → press Enter.
`client.get(url)` sends a GET request to `/loginpage/`.
The result is stored in `response` — an object containing everything Django returned:
- `response.status_code` — the HTTP status number
- `response.content` — the raw HTML bytes
- `response.context` — the data passed to the template
- `response.templates` — which templates were used

#### `assert response.status_code == 200`

**`assert` is the most important word in testing.**

```
assert <something>
If <something> is True  → test PASSES ✅
If <something> is False → test FAILS  ❌ with a clear error message
```

`response.status_code == 200` is a comparison. It returns `True` or `False`.

HTTP status codes (memorise these):
```
200 → OK (page loaded successfully)
302 → Redirect (being sent to another URL)
403 → Forbidden (not allowed to access this)
404 → Not Found (page does not exist)
500 → Internal Server Error (Django crashed)
```

This test says: "The login page MUST return 200. If it returns anything else, something is broken."

---

### Test 2: `test_login_page_uses_correct_template`

```python
def test_login_page_uses_correct_template(self, client):
    url = reverse('loginpage')
    response = client.get(url)
    assert response.status_code == 200
    assert 'htmlfiles/login.html' in [t.name for t in response.templates]
```

#### `response.templates`
A list of all template objects that Django used to render this response.
If the view did `render(request, 'htmlfiles/login.html', {...})`,
then `response.templates` contains that template.

#### `[t.name for t in response.templates]`
This is a **list comprehension** — a compact way to loop and build a list.

The long version of the same thing:
```python
template_names = []
for t in response.templates:
    template_names.append(t.name)
```

The short version (list comprehension):
```python
template_names = [t.name for t in response.templates]
```

Both produce the same list: `['htmlfiles/login.html', 'base.html', ...]`

Read it as: "give me `t.name` for every `t` in `response.templates`"

#### `assert 'htmlfiles/login.html' in [...]`
`in` checks if something exists in a list.
```python
'apple' in ['apple', 'banana']  → True
'mango' in ['apple', 'banana']  → False
```

This assert says: "The template `htmlfiles/login.html` MUST be in the list of used templates."
If someone changes the view to use a different template, this test fails and tells you immediately.

---

### Test 3: `test_login_page_has_form`

```python
def test_login_page_has_form(self, client):
    url = reverse('loginpage')
    response = client.get(url)
    assert 'form' in response.context
```

#### `response.context`
The **dictionary** Django passed to the template in `views.py`.

In `loginForm_view`:
```python
return render(request, 'htmlfiles/login.html', {'form': form})
#                                                ↑ this is the context
```

So `response.context` is `{'form': <loginForm object>}`.

#### `assert 'form' in response.context`
Checks that the key `'form'` exists in the context dictionary.

What could go wrong? If a developer changes the view to:
```python
return render(request, 'htmlfiles/login.html', {'login_form': form})
#                                                ↑ different key name!
```

The template would crash because it expects `{{ form }}` but gets `{{ login_form }}`.
This test catches that mistake immediately.

---

## GROUP 2 — `class TestLoginPOST`

POST requests are form submissions. The user filled in the form and clicked the button.

---

### Test 4: `test_empty_form_submission_stays_on_login_page`

```python
def test_empty_form_submission_stays_on_login_page(self, client):
    url = reverse('loginpage')
    response = client.post(url, data={
        'loginemail': '',
        'loginpassword': ''
    })
    assert response.status_code == 200
```

#### `client.post(url, data={...})`
Simulates submitting a form.
- `url` = where to submit
- `data={}` = the form fields (key = field name, value = what user typed)

`'loginemail': ''` means the email field is blank (user typed nothing).
`'loginpassword': ''` means the password field is blank.

The field names (`loginemail`, `loginpassword`) must match EXACTLY what is in `forms.py`.

#### `assert response.status_code == 200`
Expected: stay on the login page (200), NOT redirect (302).
Empty form = invalid = should show errors = should stay on same page.

---

### Test 5: `test_login_with_nonexistent_email_shows_error`

```python
def test_login_with_nonexistent_email_shows_error(self, client, db):
    url = reverse('loginpage')
    response = client.post(url, data={
        'loginemail': 'nobody@example.com',
        'loginpassword': 'StrongPass123!'
    })
    assert response.status_code == 200
    messages_list = list(response.wsgi_request._messages)
    assert len(messages_list) > 0
    message_texts = [str(m) for m in messages_list]
    assert any('not found' in text.lower() or 'check' in text.lower()
               for text in message_texts)
```

#### `client, db` — two fixtures
`client` = fake browser (GET/POST requests)
`db` = gives this test database access (needed because the view tries to look up the user)

#### Why `StrongPass123!` not a simple password?
Your `loginForm.clean()` in `forms.py` validates the PASSWORD FORMAT first.
If the password fails validation, the view never even tries to check if the user exists.
To test "user not found", we need the form to PASS password validation first.
So we send a strong valid-format password, and the test reaches the user-lookup stage.
This teaches you: tests force you to understand your own code flow deeply.

#### `response.wsgi_request._messages`
Django has a **messages framework** — a way for views to show one-time alerts to users.
In `views.py` there is probably code like:
```python
messages.error(request, "User not found! Please check your email.")
```
These messages are stored in `response.wsgi_request._messages`.

`_messages` starts with `_` which in Python convention means "internal/private".
But in tests we need to inspect it directly.

#### `list(response.wsgi_request._messages)`
`_messages` is a special iterable object (not a regular Python list).
`list(...)` converts it to a regular Python list so we can check `len()`, loop over it, etc.

#### `assert len(messages_list) > 0`
`len()` = how many items in the list.
```python
len([])             = 0  (empty list)
len(['hello'])      = 1
len(['a', 'b', 'c']) = 3
```
`> 0` means "at least one message must exist".

#### `message_texts = [str(m) for m in messages_list]`
Same list comprehension pattern as before.
`str(m)` converts each message object to its text string.
Result: `['User not found! Please check your email.']`

#### `assert any('not found' in text.lower() or 'check' in text.lower() for text in message_texts)`

**`any(...)` function:**
Returns `True` if AT LEAST ONE item in the loop is `True`.
Returns `False` only if ALL items are `False`.

```python
any([True, False, False])  → True   (at least one True)
any([False, False, False]) → False  (all are False)
```

**`text.lower()`** converts text to lowercase before checking.
Why? "NOT FOUND" and "not found" and "Not Found" should all match.
`.lower()` makes the check case-insensitive.

**`'not found' in text.lower()`** checks if the string "not found" appears anywhere in the message.

**Why not check the exact message text?**
```python
# Bad — fragile:
assert message_texts[0] == "User not found! Please check your email."
# If someone changes the wording slightly → test breaks

# Good — flexible:
assert any('not found' in text.lower() or 'check' in text.lower() for text in message_texts)
# Checks for the CONCEPT (user was not found), not the exact wording
```

---

### Test 6: `test_login_with_wrong_password_shows_error`

```python
def test_login_with_wrong_password_shows_error(self, client, test_user):
    url = reverse('loginpage')
    response = client.post(url, data={
        'loginemail': 'testuser@example.com',
        'loginpassword': 'WrongPassword999!'
    })
    assert response.status_code == 200
    messages_list = list(response.wsgi_request._messages)
    message_texts = [str(m) for m in messages_list]
    assert any('wrong' in text.lower() or 'password' in text.lower()
               or 'inactive' in text.lower() for text in message_texts)
```

#### `test_user` fixture
Notice `test_user` is a parameter. pytest automatically runs the `test_user` fixture first,
creating a user with `email='testuser@example.com'` in the test DB.
NOW the email lookup in the view will SUCCEED — the user exists.
But we send `'WrongPassword999!'` — a different password.
Result: authentication fails → error message shown → stay on page.

The guaranteed order of operations:
```
1. pytest runs test_user fixture → creates user in DB
2. Our test POSTs with correct email but wrong password
3. View finds the user (email exists) but authenticate() returns None (wrong password)
4. View shows error message
5. We check the error message appeared
```

---

### Test 7: `test_successful_login_redirects_to_home`

```python
def test_successful_login_redirects_to_home(self, client, test_user):
    url = reverse('loginpage')
    response = client.post(url, data={
        'loginemail': 'testuser@example.com',
        'loginpassword': 'StrongPass123!'
    })
    assert response.status_code == 302
    assert response['Location'] == '/home/'
```

#### `assert response.status_code == 302`
The HAPPY PATH — correct email + correct password.
Django's `redirect()` returns HTTP 302.

```
200 = "Here is the page"
302 = "I am not giving you a page — go to this OTHER URL instead"
```

When your view does `return redirect('/home/')`, Django sends back:
```
HTTP/1.1 302 Found
Location: /home/
```

The browser then automatically requests `/home/`.
But in tests, we see the 302 BEFORE the browser would follow it.

#### `assert response['Location'] == '/home/'`
`response['Location']` — accesses the `Location` HTTP header.
This header contains the URL the redirect is pointing to.
We verify it is pointing to `/home/` and not some other page.

**Reading response headers:**
`response['HeaderName']` syntax reads HTTP headers (like a dictionary).
Common headers you might check:
- `response['Location']` — redirect target
- `response['Content-Type']` — what type of content was returned

---

### Test 8: `test_successful_login_user_is_authenticated`

```python
def test_successful_login_user_is_authenticated(self, client, test_user):
    url = reverse('loginpage')
    response = client.post(url, data={
        'loginemail': 'testuser@example.com',
        'loginpassword': 'StrongPass123!'
    }, follow=True)
    assert response.wsgi_request.user.is_authenticated
    assert response.wsgi_request.user.username == 'testuser'
```

#### `follow=True`
Without `follow=True`: response is the 302 redirect response (before going to /home/).
With `follow=True`: pytest-django automatically follows the redirect and response is the final page.

Why do we need this here? Because we want to check if the user is in the session.
The session is fully established during the redirect + page load sequence.

#### `response.wsgi_request.user.is_authenticated`
```
response.wsgi_request   → the HTTP request object Django processed
.user                   → the user associated with this request (from the session)
.is_authenticated       → True if logged in, False if anonymous/guest
```

**Why test this separately from Test 7?**
Test 7 checks the redirect happened. But what if:
- The view calls `redirect('/home/')` ✅
- But accidentally forgot to call `login(request, user)` ❌

Test 7 would PASS (302 happened) but the user is not actually logged in.
Test 8 catches that — it checks the SESSION was actually set.

This is the beauty of multiple small focused tests:
each test checks ONE specific thing. Together they cover everything.

---

## GROUP 3 — `class TestLoginRedirectBehaviour`

---

### Test 9: `test_unauthenticated_user_cannot_access_home`

```python
def test_unauthenticated_user_cannot_access_home(self, client):
    response = client.get('/home/')
    assert response.status_code == 302
    assert '/loginpage/' in response['Location']
```

#### What is being tested?
This tests the `@login_required` decorator on `homepage_view` in `views.py`.

`@login_required` tells Django:
"If the user is not logged in and tries to access this view, redirect them to the login page."

```python
# In views.py:
@login_required(login_url='/loginpage/')
def homepage_view(request):
    ...
```

Our `client` is a fresh fake browser with NO session (not logged in).
We directly request `/home/` without logging in first.
Expected: redirect (302) to `/loginpage/`.

#### `assert '/loginpage/' in response['Location']`
Django might add extra parameters to the redirect URL:
`/loginpage/?next=/home/`
So we use `in` to check `/loginpage/` appears SOMEWHERE in the Location,
not that it exactly equals `/loginpage/`.

---

### Test 10: `test_login_with_next_param_redirects_correctly`

```python
url = reverse('loginpage') + '?next=/audio/'
response = client.post(url, data={
    'loginemail': 'testuser@example.com',
    'loginpassword': 'StrongPass123!'
})
assert response.status_code == 302
assert response['Location'] == '/audio/'
```

#### What is `?next=/audio/`?

When Django's `@login_required` redirects you to login, it adds `?next=<original url>` to the URL.

Example flow:
```
1. You are not logged in.
2. You try to visit /audio/.
3. Django redirects you to /loginpage/?next=/audio/.
4. You log in successfully.
5. The view reads: request.GET.get('next', '/home/')
6. next = '/audio/', so you are sent to /audio/ instead of /home/.
```

This is the "take me back where I came from" feature.

#### `reverse('loginpage') + '?next=/audio/'`
String concatenation. Builds: `'/loginpage/?next=/audio/'`

We test that after login, you go to `/audio/` (the page you originally wanted),
NOT to `/home/` (the default).

---

## GROUP 4 — `class TestLoginInvalidInputs` + `@pytest.mark.parametrize`

---

### Tests 11–14 via `@pytest.mark.parametrize`

```python
@pytest.mark.parametrize('email, password', [
    ('',                    ''               ),
    ('notanemail',          'somepassword'   ),
    ('a' * 200 + '@x.com',  'password'       ),
    ('test@example.com',    ''               ),
])
def test_invalid_form_data_stays_on_login_page(self, client, email, password):
    url = reverse('loginpage')
    response = client.post(url, data={
        'loginemail': email,
        'loginpassword': password
    })
    assert response.status_code == 200
```

#### `@pytest.mark.parametrize`

Without parametrize, you would write 4 separate tests:
```python
def test_empty_inputs(self, client):
    response = client.post(url, data={'loginemail': '', 'loginpassword': ''})
    assert response.status_code == 200

def test_invalid_email(self, client):
    response = client.post(url, data={'loginemail': 'notanemail', 'loginpassword': 'somepassword'})
    assert response.status_code == 200

# ... and 2 more almost identical functions — lots of repetition!
```

With `@pytest.mark.parametrize`, you write it ONCE and it runs multiple times:
```python
@pytest.mark.parametrize('email, password', [
    (value1, value2),   ← run 1
    (value1, value2),   ← run 2
    ...
])
def test_something(self, client, email, password):
    # same code, different data each time
```

#### `'email, password'`
A string listing the parameter names, separated by commas.
These become the extra parameter names in the function signature.

#### The list of tuples
Each tuple = one complete test run.
```python
('', '')                     # run 1: both empty
('notanemail', 'somepassword') # run 2: invalid email format
('a' * 200 + '@x.com', 'password') # run 3: email too long
('test@example.com', '')     # run 4: password empty
```

#### `'a' * 200 + '@x.com'`
Python string multiplication: `'a' * 3 = 'aaa'`
So `'a' * 200` = a string of 200 'a' characters.
Plus `'@x.com'` = total of 206 characters.
This tests that very long emails are rejected by your form validation.

#### What you see in test output:
```
PASSED TestLoginInvalidInputs::test_invalid_form_data_stays_on_login_page[ - ]
PASSED TestLoginInvalidInputs::test_invalid_form_data_stays_on_login_page[notanemail-somepassword]
PASSED TestLoginInvalidInputs::test_invalid_form_data_stays_on_login_page[aaa...@x.com-password]
PASSED TestLoginInvalidInputs::test_invalid_form_data_stays_on_login_page[test@example.com-]
```
Each run is listed separately with its parameter values shown in brackets.

---

## GROUP 5 — `class TestLoginMocking`

### Test 15: `test_login_calls_authenticate`

```python
def test_login_calls_authenticate(self, client, test_user):
    url = reverse('loginpage')
    response = client.post(url, data={
        'loginemail': 'testuser@example.com',
        'loginpassword': 'StrongPass123!'
    })
    assert response.status_code == 302
```

#### What is Mocking?

Some code calls **external services**:
- `send_mail()` — sends a real email
- `boto3.upload_file()` — uploads to real AWS S3
- `requests.get('https://api.example.com')` — calls a real external API

In tests, you **do NOT want** to:
- Actually send emails (creates spam)
- Actually upload files (costs money, is slow)
- Actually call external APIs (rate limits, costs, network issues)

**Mocking** = replace the real function with a fake "pretend" version you control.

#### The full mocking syntax (for your future learning):

```python
from unittest.mock import patch

# @patch replaces 'webapp.views.authenticate' with a fake during this test only
@patch('webapp.views.authenticate')
def test_login_calls_authenticate(self, mock_auth, client, test_user):
    #                               ↑ mock_auth is the fake version of authenticate

    mock_auth.return_value = test_user  # fake: when called, always return our test user

    url = reverse('loginpage')
    response = client.post(url, data={
        'loginemail': 'testuser@example.com',
        'loginpassword': 'StrongPass123!'
    })

    # Verify authenticate was actually called (not accidentally skipped)
    mock_auth.assert_called_once()
```

The important rule: **patch it where it is USED, not where it is defined.**
`authenticate` is defined in `django.contrib.auth`.
But it is USED in `webapp.views` (your view imports and calls it).
So you patch `'webapp.views.authenticate'`.

For now, our test indirectly proves `authenticate` was called:
if authenticate was not called, login could not succeed and we would get 200, not 302.
Future test files will demonstrate full mocking with signup emails, S3 uploads, etc.

---

# 📄 FILE 5 — `webapp/urls.py` (MODIFIED)

**What changed:** Added `name=` to URL patterns.

```python
# BEFORE:
path('loginpage/', views.loginForm_view),
path('home/', views.homepage_view),

# AFTER:
path('loginpage/', views.loginForm_view, name='loginpage'),
path('home/', views.homepage_view, name='home'),
```

**Why?**
`reverse('loginpage')` used in tests looks up the URL by its `name=`.
Without `name=`, `reverse()` raises `NoReverseMatch` and ALL tests fail immediately.

**Bonus benefit (not just for tests):**
- In templates: `{% url 'loginpage' %}` instead of hardcoding `/loginpage/`
- In views: `redirect('home')` instead of hardcoding `/home/`

If you ever rename `/loginpage/` to `/login/`, you change `urls.py` ONCE.
Everything else — templates, tests, views — automatically updates via `name=`.

---

# 📄 FILE 6 — `webapp/forms.py` (BUG FIXED)

**This is the most important part — tests found a REAL hidden bug.**

---

## The Bug

**In `loginForm.clean()` — before the fix:**

```python
def clean(self):
    total_cleaned_data = super().clean()
    loginemail = total_cleaned_data['loginemail']       # ← BUG: direct [] access
    loginpassword = total_cleaned_data['loginpassword'] # ← BUG: direct [] access
    bothandler = total_cleaned_data['bothandler']       # ← BUG: direct [] access
```

**After the fix:**

```python
def clean(self):
    total_cleaned_data = super().clean()
    loginemail = total_cleaned_data.get('loginemail', '')       # ← FIXED: .get()
    loginpassword = total_cleaned_data.get('loginpassword', '') # ← FIXED: .get()
    bothandler = total_cleaned_data.get('bothandler', '')       # ← FIXED: .get()
```

---

## Why Does This Matter?

### Understanding Django form validation — two stages:

**Stage 1 — Each field validates individually:**
```
loginemail field is empty → field validation FAILS → 'loginemail' REMOVED from cleaned_data
loginpassword field is empty → field validation FAILS → 'loginpassword' REMOVED from cleaned_data
```

**Stage 2 — The `clean()` method runs on whatever survived Stage 1:**
```
clean() tries to read total_cleaned_data['loginemail']
But 'loginemail' was removed in Stage 1!
Result: KeyError CRASH → Django returns HTTP 500
```

---

## Dictionary Access: `[]` vs `.get()`

```python
my_dict = {'name': 'Kalyan'}

# Direct access with []:
my_dict['name']   → 'Kalyan'         ✅ works
my_dict['email']  → KeyError CRASH!  ❌ key does not exist — program crashes

# Safe access with .get():
my_dict.get('name', '')   → 'Kalyan' ✅ works, key exists
my_dict.get('email', '')  → ''       ✅ returns the default '' — no crash
```

`.get('key', default)` means:
"Give me the value for this key.
If the key does not exist, give me the default value instead of crashing."

---

## Why Did This Bug Not Show Up in the Browser Before?

In a real browser, HTML forms have a `required` attribute:
```html
<input type="email" name="loginemail" required>
```

The browser itself **blocks** the form submission if the field is empty.
The form never even reaches Django.

But tests bypass the browser entirely. They send raw POST data directly to Django.
So the empty submission reaches Django → Stage 1 removes the key → Stage 2 crashes.

**This is a perfect example of why testing matters:**
Your app worked fine in the browser for months.
But there was a hidden crash waiting.
If anyone bypassed client-side validation (using Postman, curl, a browser with JS disabled,
or a malicious/automated request), your server would return a 500 error.
Tests found this. Tests fixed this. ✅

---

# 🗄️ The Test Database — Your Real Data is ALWAYS Safe

## Why does the test user NOT appear in your real database?

When you run `pytest`, here is the full sequence:

```
Step 1: pytest reads pytest.ini → loads Django settings
           ↓
Step 2: pytest-django creates a BRAND NEW temporary database
        (completely separate from your real db.sqlite3 or PostgreSQL)
           ↓
Step 3: Django runs all migrations on the temporary database
        (creates all the tables fresh and empty)
           ↓
Step 4: conftest.py fixtures run → testuser is created in TEMP DB only
           ↓
Step 5: All 15 tests run against the TEMP DB
           ↓
Step 6: Tests finish → pytest-django DESTROYS the temporary database completely
           ↓
Step 7: Your real database is exactly as it was — completely untouched
```

Your real `auth_user` table has your real users (KALYAN, C7V4C4, testa).
The test user (`testuser`) only ever existed in the temporary test DB which no longer exists.

---

# 🚀 How to Run the Tests

```bash
# Run ALL 15 login tests
pytest webapp/tests/test_login_view.py

# Run ALL tests in the entire project
pytest

# Run just Group 1 (GET tests only)
pytest webapp/tests/test_login_view.py::TestLoginGET

# Run just Group 2 (POST tests only)
pytest webapp/tests/test_login_view.py::TestLoginPOST

# Run ONE specific test by full name
pytest webapp/tests/test_login_view.py::TestLoginGET::test_login_page_loads

# Run by keyword — any test whose name contains the word
pytest -k login
pytest -k redirect
pytest -k password

# Stop at the FIRST failure (useful when debugging one thing at a time)
pytest -x

# Show print() output from tests (great for debugging)
pytest -s

# Stop at first failure AND show print() output — most useful combo when debugging
pytest -x -s

# Run only tests that FAILED last time (saves time)
pytest --lf

# LIST all tests without actually running them
pytest --collect-only
```

After EVERY run, two files are automatically generated in `test-results/`:
```
test-results/custom_report.html   ← open in any browser — modern dark-theme report with charts
test-results/test.log             ← plain text log of Django logging during tests
```

For the complete commands reference, see: `deploy/09-TESTING/HOW_TO_RUN_TESTS.md`

---

# 📊 Expected Test Output (All 15 Passing)

```
============== test session starts ==============
platform win32 -- Python 3.12, pytest-8.x
django: settings: webProject.settings
rootdir: D:\webProject
collected 15 items

webapp/tests/test_login_view.py::TestLoginGET::test_login_page_loads                                        PASSED
webapp/tests/test_login_view.py::TestLoginGET::test_login_page_uses_correct_template                        PASSED
webapp/tests/test_login_view.py::TestLoginGET::test_login_page_has_form                                     PASSED
webapp/tests/test_login_view.py::TestLoginPOST::test_empty_form_submission_stays_on_login_page              PASSED
webapp/tests/test_login_view.py::TestLoginPOST::test_login_with_nonexistent_email_shows_error               PASSED
webapp/tests/test_login_view.py::TestLoginPOST::test_login_with_wrong_password_shows_error                  PASSED
webapp/tests/test_login_view.py::TestLoginPOST::test_successful_login_redirects_to_home                     PASSED
webapp/tests/test_login_view.py::TestLoginPOST::test_successful_login_user_is_authenticated                 PASSED
webapp/tests/test_login_view.py::TestLoginRedirectBehaviour::test_unauthenticated_user_cannot_access_home   PASSED
webapp/tests/test_login_view.py::TestLoginRedirectBehaviour::test_login_with_next_param_redirects_correctly PASSED
webapp/tests/test_login_view.py::TestLoginInvalidInputs::test_invalid_form_data_stays_on_login_page[ - ]    PASSED
webapp/tests/test_login_view.py::TestLoginInvalidInputs::test_invalid_form_data_stays_on_login_page[notanemail-somepassword] PASSED
webapp/tests/test_login_view.py::TestLoginInvalidInputs::test_invalid_form_data_stays_on_login_page[aaa...@x.com-password]  PASSED
webapp/tests/test_login_view.py::TestLoginInvalidInputs::test_invalid_form_data_stays_on_login_page[test@example.com-]      PASSED
webapp/tests/test_login_view.py::TestLoginMocking::test_login_calls_authenticate                            PASSED

============== 15 passed in 3.42s ==============
```

---

# 🧠 Master Reference — Every Term Explained Simply

| Word / Concept | What It Means In Plain English |
|---|---|
| `pytest` | The tool that runs all your tests automatically |
| `pytest.ini` | Config file — tells pytest where Django settings are and how to behave |
| `__init__.py` | Empty file that makes a folder importable by Python |
| `conftest.py` | Shared tool chest — fixtures + hooks + report generator all in one file |
| `@pytest.fixture` | Label that says "this function prepares stuff for tests, not a test itself" |
| `@pytest.hookimpl` | Label that registers a function as a pytest hook implementation |
| `pytest_runtest_makereport` | Hook called after every single test — we use it to collect results |
| `pytest_sessionfinish` | Hook called once after ALL tests finish — we use it to write the HTML report |
| `hookwrapper=True` | Makes the hook wrap around pytest's own process — pause, let pytest run, resume |
| `tryfirst=True` | Run this hook before any other plugins — ensures we get the result first |
| `outcome = yield` | Pauses our hook, lets pytest do the test, then resumes with the result |
| `rep.when == 'call'` | Only capture the actual test body phase (not setup or teardown) |
| `rep.longrepr` | The full error traceback text — empty if test passed, filled if test failed |
| `_results = []` | Module-level list that collects one result dict per test during the session |
| `os.makedirs(..., exist_ok=True)` | Create a folder — do not crash if it already exists |
| `json.dumps(...)` | Convert Python list/dict to a JSON string (needed for Chart.js data) |
| `datetime.now().strftime(...)` | Format the current date/time as a readable string |
| `db` | Built-in fixture from pytest-django that unlocks test database access |
| `client` | Built-in fixture — a fake browser you can make GET/POST requests with |
| `force_login(user)` | Directly log in a user without going through the login form |
| `test_user` | Our custom fixture — creates a real User in the test DB before the test |
| `admin_user` | Our custom fixture — creates a superuser in the test DB |
| `logged_in_client` | Our custom fixture — client that is already logged in as test_user |
| `assert` | "This condition must be True — if False, fail the test immediately" |
| `reverse('name')` | Convert a URL name to a URL path: `'loginpage'` → `'/loginpage/'` |
| `client.get(url)` | Simulate opening a URL in the browser (no form submission) |
| `client.post(url, data={})` | Simulate clicking Submit on a form |
| `response.status_code` | HTTP number: 200=OK, 302=redirect, 404=not found, 500=crash |
| `response.context` | The dictionary Django passed to the template |
| `response.templates` | List of HTML templates Django used to render the response |
| `response['Location']` | The URL a redirect is sending you to |
| `response.wsgi_request.user` | The currently logged-in user for this request |
| `.is_authenticated` | True if the user is logged in, False if anonymous |
| `follow=True` | Follow redirects automatically — get the final page, not the 302 |
| `@pytest.mark.parametrize` | Run one test multiple times with different inputs |
| `any(...)` | Returns True if at least one item in the loop is True |
| `[x for x in list]` | List comprehension — short clean way to loop and build a list |
| `dict.get('key', default)` | Safe dictionary access — returns default if key is missing (no crash) |
| `'a' * 200` | Python string repetition — creates a string of 200 'a' characters |
| `unittest.mock.patch` | Replace a real function with a fake/pretend version during a test |
| Test database | Temporary DB created just for tests — your real database is never touched |
| `scope='function'` | Fixture is recreated fresh before each test — safest option (the default) |
| `create_user()` | Creates a user with a properly hashed password — always use this |
| `create_superuser()` | Creates an admin user with is_staff=True and is_superuser=True |
| `--tb=short` | Show shorter error messages on failure — easier to read than full traceback |
| `log_cli = true` | Show Django logger output in the terminal while tests run |
| `log_file = test-results/test.log` | Also write all log output to a plain text file |
| `custom_report.html` | The modern dark-theme HTML report with charts — auto-generated in test-results/ |
| `-x` | Stop pytest immediately at the first failure |
| `-s` | Show print() output from inside tests |
| `--lf` | Run only tests that failed last time |
| `--collect-only` | List all tests without running them |
| `-k word` | Run only tests whose name contains the word |

---

# 📸 Screenshots in pytest — The Full Truth

---

## Can pytest take screenshots like Selenium?

**No — and here is exactly why.**

Selenium opens a REAL browser (Chrome, Firefox).
A real browser renders pixels on screen — it draws buttons, colours, fonts, images.
Selenium can take a screenshot because there is a real visible screen to photograph.

pytest's `client` is a FAKE browser.
It never opens a window. It never draws anything.
It sends HTTP requests directly to Django and reads the response text.
There are no pixels. There is nothing to photograph.

```
Selenium flow:
  Open Chrome  →  Go to /loginpage/  →  Browser DRAWS the page  →  SCREENSHOT ✅

pytest client flow:
  client.get('/loginpage/')  →  Django returns HTML text  →  No drawing, no screen ❌
```

---

## What Can You Capture Instead? — HTML Snapshots

Even without screenshots, you can save the **actual HTML** Django returned.
Open the saved file in a browser and you see EXACTLY what the page contained.

We added a `save_response_html` fixture to `conftest.py` for this.

**How to use it in any test:**

```python
def test_login_page_loads(self, client, save_response_html):
    response = client.get(reverse('loginpage'))

    # Save the HTML — open in browser to see what the page looked like
    save_response_html(response, 'login_page_GET')

    assert response.status_code == 200
```

This saves: `test-results/html-snapshots/login_page_GET.html`

Open it in Chrome/Firefox — you see the login page HTML exactly as Django rendered it.

**More examples:**

```python
# Save what the page looks like after a failed login attempt
save_response_html(response, 'login_failed_wrong_password')

# Save what the page looks like with an empty form submission
save_response_html(response, 'login_empty_form_error')

# Save the home page after successful login
save_response_html(response, 'home_page_after_login')
```

Files are saved to:
```
test-results/
  html-snapshots/
    login_page_GET.html
    login_failed_wrong_password.html
    login_empty_form_error.html
    home_page_after_login.html
```

---

## Comparison Table — pytest vs Selenium

| | pytest + Django client | pytest + Selenium |
|---|---|---|
| Real browser opens? | ❌ No | ✅ Yes (Chrome/Firefox) |
| Screenshots of every step? | ❌ No | ✅ Yes |
| HTML snapshots? | ✅ Yes (our fixture) | ✅ Yes |
| Tests JavaScript behaviour? | ❌ No | ✅ Yes |
| Tests visual layout/CSS? | ❌ No | ✅ Yes |
| Speed | ⚡ Very fast (seconds) | 🐢 Slow (minutes) |
| Setup complexity | Simple — no extras | Complex — needs ChromeDriver |
| Best used for | Logic, forms, redirects, auth | Visual UI, JS interactions |
| What YOUR project uses | ✅ This | ❌ Not yet added |

---

## When Would You Add Selenium?

You would add Selenium testing when you want to test things that ONLY exist in a real browser:

- JavaScript that runs when you click a button
- CSS animations or dynamic content loading
- The visual appearance of the page (does the button look right?)
- Dropdown menus, modals, file uploads triggered by JS
- Testing that a user can complete a full workflow by actually clicking through it

For everything we test now (form submission, redirects, authentication, HTTP status codes, template rendering) — the `client` is faster, simpler, and more than enough.

---

## The `save_response_html` Fixture — Line by Line

```python
@pytest.fixture
def save_response_html():
```
Defines a fixture. But notice — it returns a FUNCTION, not data.
This is called a **factory fixture** — a fixture that gives you a tool to call yourself.

```python
    folder = os.path.join('test-results', 'html-snapshots')
    os.makedirs(folder, exist_ok=True)
```
Creates the `test-results/html-snapshots/` folder when the fixture is first used.
`exist_ok=True` = do not crash if folder already exists.

```python
    def _save(response, name):
```
Defines the inner function you actually call in your tests.
`response` = the Django test response (from `client.get()` or `client.post()`)
`name` = what you want the file to be called

```python
        html_content = response.content.decode('utf-8', errors='replace')
```
`response.content` = raw bytes of the HTML (like `b'<html>...'`)
`.decode('utf-8')` = convert bytes to a normal string (`'<html>...'`)
`errors='replace'` = if any character cannot be decoded, replace it safely instead of crashing.

```python
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
```
Writes the HTML string to a `.html` file.
`with open(...) as f:` = open the file, do something, close it automatically.
This is the standard Python way to write files safely.

```python
    return _save
```
Returns the inner `_save` function.
When your test says `save_response_html(response, 'name')`, it is calling this `_save` function.

---

*Last Updated: February 2026*

*Tests: 15 passing | Files created: 6 | Files modified: 3*

*New since initial setup: pytest.ini expanded with logging, conftest.py rewritten with hooks + HTML report generator + save_response_html fixture, test-results/ folder with custom_report.html and html-snapshots/*
