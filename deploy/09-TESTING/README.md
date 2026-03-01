# 09 — Testing

## What's in This Folder

| File | What It Contains |
|------|-----------------|
| `PYTEST_SESSION_EXPLAINED.md` | Complete line-by-line explanation of the pytest setup — every file created, every file modified, every concept explained in plain English |
| `PYTEST_FIXTURES_REFERENCE.md` | Complete reference of ALL built-in fixtures — pytest, pytest-django, Faker, and your own conftest.py fixtures — with real code examples for each |
| `PYTEST_VS_PYTEST_DJANGO.md` | Clear explanation of the difference between pytest (the core runner) and pytest-django (the Django plugin) — what each one provides, who owns which fixture |
| `HOW_TO_RUN_TESTS.md` | Every command to run tests — all tests, one file, one class, one specific test, keyword filter, debugging options — with copy-paste ready commands |

---

## Files Created During Pytest Setup

```
webProject/
  pytest.ini                        ← pytest configuration (root of project)
  webapp/
    tests/
      __init__.py                   ← makes tests folder a Python package
      conftest.py                   ← shared fixtures (test_user, admin_user, logged_in_client)
      test_login_view.py            ← 15 tests for loginForm_view
      test_claude.py                ← existing Claude API tests
```

---

## Files Modified During Pytest Setup

```
webapp/urls.py    → added name= to loginpage, home, audio, signupform, etc.
webapp/forms.py   → fixed KeyError bug in loginForm.clean() (found by tests!)
```

---

## How to Run Tests

```bash
# Run all tests
pytest -v

# Run just the login tests
pytest webapp/tests/test_login_view.py -v

# Run and stop at first failure
pytest -v -x

# Show print() output while running
pytest -v -s
```

---

## Current Test Results

| Test File | Tests | Passed | Failed |
|-----------|-------|--------|--------|
| `test_login_view.py` | 15 | 15 | 0 |
| `test_claude.py` | 2 | 2 | 0 |
| **Total** | **17** | **17** | **0** |

