# How to Run Tests — Every Command You Need

---

## The Pattern to Understand First

Every pytest command follows this structure:

```
pytest  <what to run>  <options>
```

You can be BROAD (run everything) or NARROW (run one specific test).

---

## Level 1 — Run ALL Tests in the Entire Project

```bash
pytest
```

Runs every single test in the whole project.
Currently that is **17 tests** across `test_login_view.py` and `test_claude.py`.

---

## Level 2 — Run ALL Tests in ONE File

```bash
pytest webapp/tests/test_login_view.py
```

Runs all **15 tests** inside `test_login_view.py` only. Ignores all other files.

---

## Level 3 — Run ALL Tests in ONE Class (Group)

```bash
pytest webapp/tests/test_login_view.py::TestLoginGET
```

Runs the **3 GET tests** only.

```bash
pytest webapp/tests/test_login_view.py::TestLoginPOST
```

Runs the **5 POST tests** only.

```bash
pytest webapp/tests/test_login_view.py::TestLoginRedirectBehaviour
```

Runs the **2 redirect tests** only.

```bash
pytest webapp/tests/test_login_view.py::TestLoginInvalidInputs
```

Runs the **4 invalid input tests** only.

```bash
pytest webapp/tests/test_login_view.py::TestLoginMocking
```

Runs the **1 mocking test** only.

---

## Level 4 — Run ONE Specific Test

```bash
pytest webapp/tests/test_login_view.py::TestLoginGET::test_login_page_loads
```

```bash
pytest webapp/tests/test_login_view.py::TestLoginGET::test_login_page_uses_correct_template
```

```bash
pytest webapp/tests/test_login_view.py::TestLoginGET::test_login_page_has_form
```

```bash
pytest webapp/tests/test_login_view.py::TestLoginPOST::test_empty_form_submission_stays_on_login_page
```

```bash
pytest webapp/tests/test_login_view.py::TestLoginPOST::test_login_with_nonexistent_email_shows_error
```

```bash
pytest webapp/tests/test_login_view.py::TestLoginPOST::test_login_with_wrong_password_shows_error
```

```bash
pytest webapp/tests/test_login_view.py::TestLoginPOST::test_successful_login_redirects_to_home
```

```bash
pytest webapp/tests/test_login_view.py::TestLoginPOST::test_successful_login_user_is_authenticated
```

```bash
pytest webapp/tests/test_login_view.py::TestLoginRedirectBehaviour::test_unauthenticated_user_cannot_access_home
```

```bash
pytest webapp/tests/test_login_view.py::TestLoginRedirectBehaviour::test_login_with_next_param_redirects_correctly
```

```bash
pytest webapp/tests/test_login_view.py::TestLoginMocking::test_login_calls_authenticate
```

---

## The :: Pattern Explained

The `::` (double colon) is how you drill down level by level:

```
pytest  filename.py                          --> ALL tests in the file
pytest  filename.py::ClassName               --> ALL tests in that class
pytest  filename.py::ClassName::method_name  --> ONE specific test only
```

Visual diagram:

```
FILE               ::  CLASS         ::  FUNCTION
test_login_view.py :: TestLoginGET  :: test_login_page_loads
      |                   |                  |
   the file            the group          the test
```

---

## Useful Options — Add to ANY Command Above

| Option | What It Does |
|--------|-------------|
| `-v` | Verbose — show each test name (already ON via pytest.ini) |
| `-s` | Show `print()` output from inside your tests |
| `-x` | Stop immediately at the FIRST failure |
| `-x -s` | Stop at first failure AND show print() — best for debugging |
| `--lf` | Run ONLY the tests that FAILED last time |
| `--ff` | Run failed tests FIRST, then the rest |
| `-k word` | Run tests whose name CONTAINS a keyword |
| `--tb=short` | Shorter error messages on failure |
| `--tb=no` | Hide error details — just show PASSED or FAILED |
| `-q` | Quiet mode — minimal output |
| `--collect-only` | LIST all tests without running them |

---

## The -k Keyword Filter — Easiest Way to Run a Group

Run any test whose name **contains** a word — without typing the full path:

```bash
pytest -k login
```

Runs every test with the word `login` in its name.

```bash
pytest -k redirect
```

Runs every test with the word `redirect` in its name.

```bash
pytest -k password
```

Runs every test with the word `password` in its name.

```bash
pytest -k "login and not redirect"
```

Runs tests with `login` in the name BUT NOT `redirect`.

---

## Quick Copy-Paste Summary

```bash
# ── RUN EVERYTHING ──────────────────────────────────────
pytest


# ── RUN ONE WHOLE FILE ──────────────────────────────────
pytest webapp/tests/test_login_view.py


# ── RUN ONE CLASS (GROUP) ───────────────────────────────
pytest webapp/tests/test_login_view.py::TestLoginGET
pytest webapp/tests/test_login_view.py::TestLoginPOST
pytest webapp/tests/test_login_view.py::TestLoginRedirectBehaviour
pytest webapp/tests/test_login_view.py::TestLoginInvalidInputs
pytest webapp/tests/test_login_view.py::TestLoginMocking


# ── RUN ONE SPECIFIC TEST ───────────────────────────────
pytest webapp/tests/test_login_view.py::TestLoginGET::test_login_page_loads
pytest webapp/tests/test_login_view.py::TestLoginPOST::test_successful_login_redirects_to_home
pytest webapp/tests/test_login_view.py::TestLoginPOST::test_successful_login_user_is_authenticated


# ── RUN BY KEYWORD ──────────────────────────────────────
pytest -k login
pytest -k redirect
pytest -k password
pytest -k authenticated


# ── DEBUGGING ───────────────────────────────────────────
pytest --lf                                   # only tests that failed last time
pytest -x                                     # stop at first failure
pytest -s                                     # show print() output
pytest -x -s                                  # stop + show print (most useful)
pytest webapp/tests/test_login_view.py -x -s  # one file with stop + print


# ── LIST ALL TESTS WITHOUT RUNNING ──────────────────────
pytest --collect-only
```

---

## How to Find the Exact Test Name

If you forget any name, run this to list everything without running anything:

```bash
pytest --collect-only
```

Output looks like:

```
<Module test_login_view.py>
  <Class TestLoginGET>
    <Function test_login_page_loads>
    <Function test_login_page_uses_correct_template>
    <Function test_login_page_has_form>
  <Class TestLoginPOST>
    <Function test_empty_form_submission_stays_on_login_page>
    <Function test_login_with_nonexistent_email_shows_error>
    <Function test_login_with_wrong_password_shows_error>
    <Function test_successful_login_redirects_to_home>
    <Function test_successful_login_user_is_authenticated>
  <Class TestLoginRedirectBehaviour>
    <Function test_unauthenticated_user_cannot_access_home>
    <Function test_login_with_next_param_redirects_correctly>
  <Class TestLoginInvalidInputs>
    <Function test_invalid_form_data_stays_on_login_page[...]>
  <Class TestLoginMocking>
    <Function test_login_calls_authenticate>
```

Copy the exact name you need and paste it into your run command.

---

*Last Updated: February 2026*
