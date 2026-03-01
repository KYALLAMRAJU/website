# pytest vs pytest-django

## What is the Difference?

---

## The Simple Analogy

Think of it like a **car and its GPS**:

| | Analogy | Role |
|---|---|---|
| **pytest** | The CAR | Runs tests for any Python project |
| **pytest-django** | The GPS | Adds Django-specific directions to the car |

The car works without GPS -- but when navigating Django, the GPS makes it far easier.

The GPS is useless without the car.

---

## pytest -- The Core Test Runner

**What it is:**

A completely general-purpose Python testing tool.
Nothing Django about it. Works with Flask, FastAPI, plain Python scripts -- anything.

**What it gives you:**

- The ability to run tests (pytest command in the terminal)
- assert keyword support with nice error messages showing exactly what failed
- @pytest.fixture -- the fixture system (prepare data before tests)
- @pytest.mark.parametrize -- run one test with many different inputs
- @pytest.mark.skip -- skip a test with a reason
- @pytest.mark.xfail -- mark a test expected to fail
- capsys, capfd, caplog -- capture output and logs
- tmp_path, tmp_path_factory -- temporary folders
- monkeypatch -- replace functions temporarily
- recwarn, cache, subtests -- warnings, caching, sub-assertions
- Reading pytest.ini config file
- A plugins system that lets pytest-django plug into it

**Installed via:**

```
pip install pytest
```

**Works on:** Any Python project. No Django needed at all.

---

## pytest-django -- The Django Plugin

**What it is:**

A PLUGIN for pytest that adds Django-specific features.

Without pytest-django, pytest has no idea what Django is.
It cannot set up the test database, cannot understand URL patterns,
and cannot make requests to your views.

**What it ADDS on top of pytest:**

- db fixture -- test database access
- transactional_db fixture -- real transactions in tests
- client fixture -- Django fake browser (TestClient)
- admin_client fixture -- client logged in as admin
- rf fixture -- Django RequestFactory
- django_user_model fixture -- the correct User model class
- admin_user fixture -- creates a superuser automatically
- settings fixture -- modify Django settings per-test and revert after
- mailoutbox fixture -- capture emails without actually sending them
- live_server fixture -- run a real Django server during tests
- django_assert_num_queries -- count DB queries a view makes
- @pytest.mark.django_db marker -- allow DB access in a test
- Reads DJANGO_SETTINGS_MODULE from pytest.ini
- Sets up and tears down the test database automatically
- Runs Django migrations before tests run

**Installed via:**

```
pip install pytest-django
```

**Works on:** Django projects ONLY.

---

## What is in YOUR Project

```
requirements.txt:

  pytest          <-- the core runner (the car)
  pytest-django   <-- the Django plugin (the GPS)
  Faker           <-- another plugin (for the faker fixture)
```

---

## How They Work Together

When you type **pytest** in your terminal, here is what happens step by step:

**Step 1:** pytest (core) starts up

**Step 2:** pytest reads pytest.ini

**Step 3:** pytest-django reads DJANGO_SETTINGS_MODULE from pytest.ini

**Step 4:** pytest-django starts Django using webProject/settings.py

**Step 5:** pytest-django creates the test database and runs all migrations

**Step 6:** pytest finds all test files matching test_*.py

**Step 7:** pytest runs each test, injecting fixtures:

- capsys, tmp_path, monkeypatch  -->  come from **pytest**
- db, client, mailoutbox         -->  come from **pytest-django**
- test_user, logged_in_client    -->  come from **YOUR conftest.py**

**Step 8:** All tests finish

**Step 9:** pytest-django destroys the test database completely

**Step 10:** pytest prints the final results summary

---

## Who Owns Which Fixture

| Fixture | Comes From | What It Does |
|---|---|---|
| capsys | pytest | Capture print() output |
| capfd | pytest | Capture file descriptor output |
| caplog | pytest | Capture log messages |
| monkeypatch | pytest | Replace functions/env vars temporarily |
| tmp_path | pytest | Temp folder deleted after test |
| tmp_path_factory | pytest | Session-scoped temp folder |
| recwarn | pytest | Capture Python warnings |
| cache | pytest | Persist data between test runs |
| pytestconfig | pytest | Read pytest.ini config |
| subtests | pytest | Run multiple sub-assertions |
| db | pytest-django | Test database read/write access |
| transactional_db | pytest-django | Real transaction test database |
| client | pytest-django | Django fake browser |
| admin_client | pytest-django | Fake browser logged in as admin |
| async_client | pytest-django | Async fake browser |
| rf | pytest-django | Django RequestFactory |
| async_rf | pytest-django | Async RequestFactory |
| django_user_model | pytest-django | The correct User model class |
| admin_user | pytest-django | Creates a superuser |
| settings | pytest-django | Modify Django settings per-test |
| live_server | pytest-django | Real Django server |
| mailoutbox | pytest-django | Capture emails |
| django_assert_num_queries | pytest-django | Assert exact DB query count |
| django_assert_max_num_queries | pytest-django | Assert max DB query count |
| faker | Faker plugin | Generate realistic fake data |
| test_user | YOUR conftest.py | Creates testuser in test DB |
| admin_user | YOUR conftest.py | Creates adminuser in test DB |
| logged_in_client | YOUR conftest.py | client already logged in |

---

## One Line Summary

```
pytest        = the ENGINE that RUNS tests (any Python project)
pytest-django = the ADAPTER that makes pytest UNDERSTAND Django
```

You need BOTH. One without the other does not work for Django testing.

---

## FAQ

**Q: If I work on a non-Django Python project, do I still use pytest?**

A: Yes -- just pytest alone. No pytest-django needed.

---

**Q: Can pytest-django work without pytest?**

A: No. It is a PLUGIN -- pytest must be installed first.

---

**Q: Why not just use python manage.py test?**

A: manage.py test uses Django's built-in runner (based on unittest).
pytest gives you better error messages, fixtures instead of setUp/tearDown boilerplate,
parametrize, better plugins, and much cleaner syntax.

---

**Q: What is the relationship between Django TestCase and pytest?**

A: pytest can also run old-style Django unittest.TestCase tests.
It is backwards compatible. But pytest-style tests using fixtures
and plain assert are simpler and more powerful.

---

*Last Updated: February 2026*

*pytest: 9.0.2 | pytest-django: 4.12.0 | Django: 5.2.8*
