# 📦 Complete Built-in Fixtures Reference
## Every Fixture Available in Your Project — Explained Simply

> **What is this file?**
> When writing tests, you never have to create a fake browser, a temp folder, or a test database
> from scratch. pytest and pytest-django give you ready-made fixtures for all of this.
> This file lists every single one — what it does, when to use it, and a real code example.
>
> **How to use this file:**
> Before writing a test, scan this list. If a fixture already does what you need — use it.
> If nothing fits, that's when you write your own fixture in `conftest.py`.

---

# 🗂️ CATEGORIES AT A GLANCE

| Category | Fixtures |
|---|---|
| 🗄️ **Database** (pytest-django) | `db`, `transactional_db`, `django_db_reset_sequences`, `django_db_serialized_rollback` |
| 🌐 **HTTP Client** (pytest-django) | `client`, `admin_client`, `async_client`, `rf`, `async_rf` |
| 👤 **User / Auth** (pytest-django) | `django_user_model`, `django_username_field`, `admin_user` |
| ⚙️ **Django Settings** (pytest-django) | `settings`, `live_server` |
| 📧 **Email** (pytest-django) | `mailoutbox` |
| 🔍 **DB Query Counting** (pytest-django) | `django_assert_num_queries`, `django_assert_max_num_queries` |
| 📂 **Temporary Files** (pytest built-in) | `tmp_path`, `tmp_path_factory`, `tmpdir`, `tmpdir_factory` |
| 🖨️ **Output Capturing** (pytest built-in) | `capsys`, `capfd`, `capsysbinary`, `capfdbinary`, `capteesys` |
| 📋 **Logging** (pytest built-in) | `caplog` |
| 🔧 **Patching / Mocking** (pytest built-in) | `monkeypatch` |
| ⚠️ **Warnings** (pytest built-in) | `recwarn` |
| 💾 **Cache** (pytest built-in) | `cache` |
| ⚙️ **Config** (pytest built-in) | `pytestconfig` |
| 🎲 **Fake Data** (Faker plugin) | `faker` |
| 🧪 **Sub-tests** (pytest built-in) | `subtests` |
| 🏠 **Your Own** (conftest.py) | `test_user`, `admin_user`, `logged_in_client` |

---

# 🗄️ SECTION 1 — DATABASE FIXTURES (from pytest-django)

These fixtures control whether your test can access the database and HOW.

---

## `db` ⭐ (Most Used)

**What it does:**
Gives your test READ and WRITE access to the test database.
After each test, all changes are automatically rolled back (undone).
So each test starts with a clean database.

**How rollback works:**
Django wraps the entire test in a database transaction.
When the test finishes, the transaction is rolled BACK — as if it never happened.
The next test starts fresh.

**When to use:**
- Any test that creates, reads, updates, or deletes data
- Any test that uses `User.objects.create_user()`
- Any test where your view touches the database

**Usage:**
```python
# Option 1: Use as a parameter in a fixture
@pytest.fixture
def test_user(db):
    return User.objects.create_user(username='kalyan', password='Pass123!')

# Option 2: Use directly in a test
def test_something(db):
    User.objects.create_user(username='kalyan', password='Pass123!')
    assert User.objects.count() == 1

# Option 3: Use the marker instead (older style — both work)
@pytest.mark.django_db
def test_something():
    User.objects.create_user(username='kalyan', password='Pass123!')
    assert User.objects.count() == 1
```

**Important:** `client` does NOT include `db` automatically.
If your test uses `client` AND needs the database, add BOTH:
```python
def test_something(client, db):
    ...
```
OR use a fixture that already has `db` (like `test_user`):
```python
def test_something(client, test_user):
    # test_user fixture already pulled in db access — you don't need db separately
    ...
```

---

## `transactional_db`

**What it does:**
Same as `db` BUT allows REAL database transactions in tests.

**The difference from `db`:**
```
db:               wraps test in a transaction, rolls back at end — FAST
transactional_db: actually commits and resets the DB after each test — SLOWER
```

**When to use:**
- When your view uses `transaction.atomic()` or `on_commit()` callbacks
- When you need to test Django signals that fire after a transaction commits
- When testing code that checks if a transaction committed
- When using `live_server` (required — the server runs in a different thread)

**Usage:**
```python
def test_with_real_transaction(transactional_db):
    with transaction.atomic():
        User.objects.create_user(username='kalyan', password='Pass123!')
    # Real commit happened — we can verify it
    assert User.objects.filter(username='kalyan').exists()
```

---

## `django_db_reset_sequences`

**What it does:**
Same as `transactional_db` but ALSO resets auto-increment sequences (like primary key IDs).

**The problem it solves:**
Without this, IDs keep counting up across tests:
```
Test 1: creates User → id=1
Test 2: creates User → id=2 (not id=1!)
```
With `django_db_reset_sequences`:
```
Test 1: creates User → id=1
Test 2: creates User → id=1 (reset!)
```

**When to use:**
Only when your test logic depends on SPECIFIC ID values (rare).
Most tests should not care what ID a record gets.

**Usage:**
```python
def test_first_user_has_id_one(django_db_reset_sequences):
    user = User.objects.create_user(username='kalyan', password='Pass123!')
    assert user.id == 1  # guaranteed because sequences were reset
```

---

## `django_db_serialized_rollback`

**What it does:**
Saves a snapshot of the database, runs the test, then restores from snapshot.

**When to use:**
Databases that do not support transactions (very rare).
Usually you will never need this.

---

# 🌐 SECTION 2 — HTTP CLIENT FIXTURES (from pytest-django)

These fixtures give you fake web browsers to make requests to your Django views.

---

## `client` ⭐ (Most Used)

**What it does:**
A fake web browser (Django's `TestClient`).
Can make GET, POST, PUT, DELETE requests to your Django views.
Does NOT open a real browser — it talks directly to Django, bypassing the network.
Much faster than Selenium or real browser testing.

**What it gives you:**
```python
client.get(url)                      # simulate opening a URL
client.post(url, data={})            # simulate submitting a form
client.put(url, data={}, content_type='application/json')   # PUT request
client.delete(url)                   # DELETE request
client.patch(url, data={}, content_type='application/json') # PATCH request

# Response object:
response.status_code                 # 200, 302, 403, 404, 500 etc.
response.content                     # raw HTML bytes
response.context                     # template context dictionary
response.templates                   # list of templates used
response['Location']                 # redirect URL (from Location header)
response.wsgi_request.user           # the currently logged-in user
response.json()                      # parse JSON response (for API views)
```

**When to use:**
For any test that needs to make HTTP requests to your views.
This is the fixture you will use in 90% of your tests.

**Important:** `client` is NOT logged in by default.
It is like a fresh anonymous browser tab with no session.

**Usage:**
```python
def test_login_page_loads(client):
    response = client.get('/loginpage/')
    assert response.status_code == 200

def test_submit_form(client):
    response = client.post('/loginpage/', data={
        'loginemail': 'test@example.com',
        'loginpassword': 'Pass123!'
    })
    assert response.status_code == 302  # redirect after success

# Logging in manually within a test:
def test_home_page(client, test_user):
    client.force_login(test_user)       # log in without a form
    response = client.get('/home/')
    assert response.status_code == 200

# Following redirects automatically:
def test_with_redirect(client, test_user):
    client.force_login(test_user)
    response = client.get('/home/', follow=True)  # follow=True follows all redirects
    assert response.status_code == 200
```

---

## `admin_client` ⭐

**What it does:**
Same as `client` but ALREADY logged in as an admin user (superuser).
The admin user is created automatically with username `admin` and password `password`.

**When to use:**
When testing views that require `@staff_member_required` or `is_superuser`.
When testing the Django admin panel pages.

**Usage:**
```python
def test_admin_panel_loads(admin_client):
    response = admin_client.get('/admin/')
    assert response.status_code == 200

def test_admin_only_view(admin_client):
    response = admin_client.get('/admin-dashboard/')
    assert response.status_code == 200  # only admins can see this
```

---

## `async_client`

**What it does:**
Same as `client` but for **async** Django views (views using `async def`).

**When to use:**
Only if you have `async def` views in your `views.py`.
For normal synchronous views, use regular `client`.

**Usage:**
```python
@pytest.mark.asyncio
async def test_async_view(async_client):
    response = await async_client.get('/some-async-view/')
    assert response.status_code == 200
```

---

## `rf` (RequestFactory)

**What it does:**
Builds HTTP request objects WITHOUT going through Django's URL routing, middleware, or sessions.

**The difference from `client`:**
```
client:  request → URL routing → middleware → view → full Django response
rf:      request object only — you pass it directly to the view function yourself
```

**When to use:**
When you want to test a VIEW FUNCTION directly, in complete isolation,
without Django's URL patterns or middleware running.
Useful for unit testing individual view functions.

**Usage:**
```python
from webapp.views import homepage_view

def test_homepage_view_directly(rf, test_user):
    request = rf.get('/home/')           # build a GET request object
    request.user = test_user             # manually set the user (no session)
    response = homepage_view(request)    # call the view directly
    assert response.status_code == 200
```

**Note:** Because middleware does NOT run, things like `request.session`,
`messages`, and `@login_required` do not work automatically.
Use `client` for integration tests. Use `rf` for true unit tests of individual views.

---

## `async_rf` (Async RequestFactory)

**What it does:**
Same as `rf` but for async views.
Only needed if you have `async def` views.

---

# 👤 SECTION 3 — USER / AUTH FIXTURES (from pytest-django)

---

## `django_user_model` ⭐

**What it does:**
Returns the User MODEL CLASS configured in your Django settings.
Automatically handles custom User models.

**Why it exists:**
If you have a custom User model defined in `settings.py`:
```python
AUTH_USER_MODEL = 'webapp.CustomUser'
```
Using `from django.contrib.auth.models import User` would be WRONG — it would be the
wrong model. `django_user_model` always gives you the correct model regardless.

**When to use:**
Whenever you need to create users in tests — especially if you might ever switch
to a custom User model. It is better practice than importing User directly.

**Usage:**
```python
def test_create_user(django_user_model):
    user = django_user_model.objects.create_user(
        username='kalyan',
        password='Pass123!'
    )
    assert user.username == 'kalyan'

# You can also use it in fixtures:
@pytest.fixture
def test_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username='testuser',
        password='Pass123!'
    )
```

---

## `django_username_field`

**What it does:**
Returns the name of the username field on the User model as a string.
Default Django: `'username'`.
If you use email as username: `'email'`.

**When to use:**
When writing generic fixtures that work with ANY User model configuration.
Rarely needed unless building reusable test helpers.

**Usage:**
```python
def test_username_field(django_username_field):
    assert django_username_field == 'username'  # or 'email' for custom models
```

---

## `admin_user` (built-in pytest-django version)

**What it does:**
Creates (or retrieves if already exists) a superuser with:
- username: `admin`
- password: `password`

**Note:** This is the BUILT-IN version from pytest-django.
Your `conftest.py` also defines an `admin_user` fixture which OVERRIDES this one.
Your version uses more secure credentials (`AdminPass123!`).

**When to use:**
Use your `conftest.py` version (it's already loaded automatically).
The built-in version is there as a fallback.

---

# ⚙️ SECTION 4 — DJANGO SETTINGS FIXTURE (from pytest-django)

---

## `settings` ⭐

**What it does:**
Gives you a live Django settings object that you can MODIFY for a single test.
All changes are automatically reversed after the test — your real settings are never permanently changed.

**When to use:**
- Testing how your app behaves with different settings values
- Testing `DEBUG = True` vs `DEBUG = False` behaviour
- Testing different `EMAIL_BACKEND` configurations
- Testing feature flags in settings

**Usage:**
```python
def test_with_debug_off(client, settings):
    settings.DEBUG = False
    response = client.get('/nonexistent-page/')
    assert response.status_code == 404  # proper 404, not debug page

def test_email_setting(settings, mailoutbox):
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    # now emails go to mailoutbox instead of being sent for real

def test_allowed_hosts(settings):
    settings.ALLOWED_HOSTS = ['testserver', 'localhost']
    # test with specific ALLOWED_HOSTS

def test_cache_disabled(settings):
    settings.CACHES = {
        'default': {'BACKEND': 'django.core.cache.backends.dummy.DummyCache'}
    }
    # cache is disabled for this test only
```

---

## `live_server`

**What it does:**
Starts a REAL Django web server on a real port (e.g. `http://localhost:54321`) in the background.
Other tools (like Selenium browser testing) can connect to it as a real HTTP server.

**When to use:**
- End-to-end browser testing with Selenium
- Testing WebSockets
- Testing behaviour that specifically requires a real HTTP connection

**Usage:**
```python
def test_with_selenium(live_server):
    # live_server.url is something like 'http://localhost:54321'
    url = live_server.url + '/loginpage/'
    # selenium_driver.get(url)  ← open in real browser
    print(live_server.url)      # e.g. http://localhost:54321

# Important: requires transactional_db if the view touches the database
def test_with_real_server(live_server, transactional_db):
    response = requests.get(live_server.url + '/home/')
    assert response.status_code == 302
```

---

# 📧 SECTION 5 — EMAIL FIXTURE (from pytest-django)

---

## `mailoutbox` ⭐

**What it does:**
Captures all emails Django sends during a test WITHOUT actually sending them.
You can inspect what was "sent" and verify the content.

**When to use:**
Any time your view sends an email:
- Registration confirmation email
- Password reset email
- Contact form email (`contactusForm`)
- Any `send_mail()` or `EmailMessage().send()` call

**Usage:**
```python
def test_signup_sends_confirmation_email(client, db, mailoutbox):
    response = client.post('/signup/', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'StrongPass123!'
    })

    # Check one email was sent
    assert len(mailoutbox) == 1

    # Check who it was sent to
    email = mailoutbox[0]
    assert email.to == ['newuser@example.com']

    # Check the subject
    assert 'Welcome' in email.subject or 'Confirm' in email.subject

    # Check the body contains something
    assert 'newuser@example.com' in email.body

def test_password_reset_email(client, db, mailoutbox):
    User.objects.create_user(username='kalyan', email='kalyan@test.com', password='Pass123!')
    client.post('/reset-password/', data={'email': 'kalyan@test.com'})
    assert len(mailoutbox) == 1
    assert mailoutbox[0].to == ['kalyan@test.com']

def test_contact_form_sends_email(client, mailoutbox):
    client.post('/contact/', data={
        'name': 'Kalyan',
        'email': 'kalyan@test.com',
        'message': 'Hello!'
    })
    assert len(mailoutbox) == 1
    assert 'Hello!' in mailoutbox[0].body

# Check NO email was sent
def test_failed_login_no_email(client, db, mailoutbox):
    client.post('/loginpage/', data={
        'loginemail': 'wrong@example.com',
        'loginpassword': 'WrongPass123!'
    })
    assert len(mailoutbox) == 0  # login failure should NOT send an email
```

---

# 🔍 SECTION 6 — DB QUERY COUNTING (from pytest-django)

---

## `django_assert_num_queries` ⭐

**What it does:**
Asserts that a block of code makes EXACTLY a specific number of database queries.
Fails the test if the count is different.

**When to use:**
- Performance testing — catching the N+1 query problem
- Making sure a view is not making more DB queries than expected
- Verifying `select_related()` and `prefetch_related()` are working

**What is the N+1 problem?**
Imagine a view that loads 10 users, then for each user loads their posts separately:
```python
users = User.objects.all()       # 1 query
for user in users:
    posts = user.posts.all()     # 10 separate queries (one per user!) = N+1 problem
```
This is 11 queries instead of 2. With 100 users it's 101 queries. It destroys performance.
`select_related()` or `prefetch_related()` fixes it to 2 queries.
`django_assert_num_queries` helps you catch and verify this.

**Usage:**
```python
def test_home_page_query_count(client, test_user, django_assert_num_queries):
    client.force_login(test_user)
    with django_assert_num_queries(3):  # expect exactly 3 DB queries
        response = client.get('/home/')
    assert response.status_code == 200

def test_efficient_list_view(client, db, django_assert_num_queries):
    # Create 5 users
    for i in range(5):
        User.objects.create_user(username=f'user{i}', password='Pass123!')
    with django_assert_num_queries(2):  # should only be 2 queries even with 5 users
        response = client.get('/users-list/')
```

---

## `django_assert_max_num_queries`

**What it does:**
Same as `django_assert_num_queries` but sets an UPPER LIMIT — passes as long as the
number of queries does not EXCEED the limit. More forgiving.

**Usage:**
```python
def test_home_page_max_queries(client, test_user, django_assert_max_num_queries):
    client.force_login(test_user)
    with django_assert_max_num_queries(10):  # must use 10 or fewer queries
        response = client.get('/home/')
    assert response.status_code == 200
```

---

# 📂 SECTION 7 — TEMPORARY FILE FIXTURES (pytest built-in)

---

## `tmp_path` ⭐

**What it does:**
Gives your test a temporary folder (as a `pathlib.Path` object) that is unique
to each test and automatically deleted after the test.

**When to use:**
- Testing file upload handling
- Testing CSV/Excel export features
- Testing anything that reads/writes files
- Any test that needs a real folder to work with

**Usage:**
```python
def test_file_upload(client, test_user, tmp_path):
    # Create a fake file to upload
    test_file = tmp_path / 'test_audio.mp3'
    test_file.write_bytes(b'fake mp3 content')

    client.force_login(test_user)
    with open(test_file, 'rb') as f:
        response = client.post('/upload-audio/', {'file': f})
    assert response.status_code == 200

def test_csv_export(client, test_user, tmp_path):
    client.force_login(test_user)
    response = client.get('/export-users-csv/')
    # Save the CSV to temp file and verify it
    csv_file = tmp_path / 'export.csv'
    csv_file.write_bytes(response.content)
    content = csv_file.read_text()
    assert 'username' in content

def test_write_read_file(tmp_path):
    file = tmp_path / 'hello.txt'
    file.write_text('Hello World')
    assert file.read_text() == 'Hello World'
    # tmp_path/hello.txt is automatically deleted after this test
```

---

## `tmp_path_factory` (session scope)

**What it does:**
Same as `tmp_path` but for SESSION-SCOPED fixtures that need a temp folder
shared across multiple tests.

**When to use:**
When you need a temp folder that persists across multiple tests (not cleaned between tests).
Rarely needed — use `tmp_path` for almost everything.

**Usage:**
```python
@pytest.fixture(scope='session')
def shared_temp_folder(tmp_path_factory):
    folder = tmp_path_factory.mktemp('shared_data')
    # Create files that all tests in the session can share
    (folder / 'test_data.json').write_text('{"key": "value"}')
    return folder
```

---

## `tmpdir` (Legacy — use `tmp_path` instead)

**What it does:**
Old version of `tmp_path`. Returns a `py.path.local` object instead of `pathlib.Path`.
Still works but `tmp_path` is preferred in modern Python.

---

# 🖨️ SECTION 8 — OUTPUT CAPTURING FIXTURES (pytest built-in)

---

## `capsys` ⭐

**What it does:**
Captures everything your code prints to the terminal (stdout/stderr) during a test.
Lets you assert on what was printed.

**When to use:**
- Testing that your code prints the right things (like management commands)
- Verifying `print()` debug statements in your code
- Testing CLI scripts

**Usage:**
```python
def test_view_prints_debug_info(capsys):
    # Run code that prints something
    print("DEBUG: user logged in")

    # Read what was captured
    captured = capsys.readouterr()

    assert captured.out == "DEBUG: user logged in\n"
    assert captured.err == ""  # nothing printed to stderr

# Real Django example: management command
from django.core.management import call_command
def test_management_command_output(capsys):
    call_command('my_custom_command')
    captured = capsys.readouterr()
    assert 'Success' in captured.out

# You can also disable capturing to see output in real time:
def test_with_output(capsys):
    print("this will be captured")
    with capsys.disabled():
        print("this will print to terminal even during test")
```

---

## `capfd`

**What it does:**
Same as `capsys` but captures at the file descriptor level (lower level).
Captures output even from C extensions or subprocesses that write directly
to file descriptor 1 (stdout) or 2 (stderr).

**When to use:**
Only when `capsys` is not capturing something — very rare in Django projects.

---

## `capsysbinary`

**What it does:**
Same as `capsys` but captures as BYTES instead of text.
Useful when the output is binary (not normal text).

**Usage:**
```python
def test_binary_output(capsysbinary):
    sys.stdout.buffer.write(b'\x00\x01\x02')
    captured = capsysbinary.readouterr()
    assert captured.out == b'\x00\x01\x02'
```

---

## `capfdbinary`

**What it does:**
Same as `capfd` (file descriptor level) but captures as bytes.
Almost never needed in Django projects.

---

## `capteesys`

**What it does:**
Same as `capsys` but ALSO lets the output pass through to the terminal (tee = copy).
So output is both captured AND printed to the screen at the same time.

**Usage:**
```python
def test_something(capteesys):
    print("this appears in terminal AND is captured")
    captured = capteesys.readouterr()
    assert 'this appears' in captured.out
```

---

# 📋 SECTION 9 — LOGGING FIXTURE (pytest built-in)

---

## `caplog` ⭐

**What it does:**
Captures log messages (from Python's `logging` module) during a test.
Lets you verify your views/functions are logging the right things.

**When to use:**
- Your views use `logger.info(...)`, `logger.error(...)`, `logger.warning(...)` etc.
- You want to verify errors are being logged
- Testing logging behaviour without actually writing to a log file

**Usage:**
```python
import logging

def test_login_failure_is_logged(client, db, caplog):
    with caplog.at_level(logging.WARNING):
        response = client.post('/loginpage/', data={
            'loginemail': 'nobody@example.com',
            'loginpassword': 'StrongPass123!'
        })

    # Check a warning was logged
    assert len(caplog.records) > 0
    assert any('not found' in record.message.lower()
               for record in caplog.records)

def test_successful_login_not_logged_as_error(client, test_user, caplog):
    with caplog.at_level(logging.ERROR):
        client.post('/loginpage/', data={
            'loginemail': 'testuser@example.com',
            'loginpassword': 'StrongPass123!'
        })
    # No errors should be logged on successful login
    assert len(caplog.records) == 0

# What caplog gives you:
# caplog.records          → list of LogRecord objects
# caplog.messages         → list of just the message strings
# caplog.text             → all log output as one string
# caplog.record_tuples    → list of (logger_name, level, message)
# caplog.clear()          → clear all captured records
```

---

# 🔧 SECTION 10 — MONKEYPATCHING FIXTURE (pytest built-in)

---

## `monkeypatch` ⭐

**What it does:**
Temporarily replaces/modifies anything in your code:
- Replace a function with a fake one
- Change a class attribute
- Set/delete environment variables
- Modify `sys.path`

All changes are automatically undone after the test.

**Difference from `unittest.mock.patch`:**
Both do similar things. `monkeypatch` is simpler but less powerful.
`unittest.mock.patch` is more flexible and commonly used for complex mocking.
For simple replacements, `monkeypatch` is cleaner.

**Usage:**
```python
# 1. Replace a function:
def fake_send_mail(*args, **kwargs):
    return 1  # pretend it always succeeds

def test_signup_sends_email(client, db, monkeypatch):
    monkeypatch.setattr('django.core.mail.send_mail', fake_send_mail)
    response = client.post('/signup/', data={...})
    assert response.status_code == 302
    # real email was never sent — fake_send_mail was called instead

# 2. Set environment variables:
def test_with_env_var(monkeypatch):
    monkeypatch.setenv('MY_SECRET_KEY', 'test-secret-value')
    import os
    assert os.environ['MY_SECRET_KEY'] == 'test-secret-value'
    # after test, MY_SECRET_KEY is removed

# 3. Delete environment variables:
def test_without_env_var(monkeypatch):
    monkeypatch.delenv('SOME_API_KEY', raising=False)
    # SOME_API_KEY is gone for this test only

# 4. Change a settings value (simpler alternative to `settings` fixture):
def test_with_changed_setting(monkeypatch, settings):
    monkeypatch.setattr(settings, 'DEBUG', False)
    # DEBUG is False for this test only

# 5. Replace a class attribute:
def test_with_mocked_storage(monkeypatch):
    monkeypatch.setattr('webapp.storages.MyStorage.save', lambda self, name, content, max_length=None: name)
    # storage.save() now just returns the filename instead of uploading to S3
```

---

# ⚠️ SECTION 11 — WARNINGS FIXTURE (pytest built-in)

---

## `recwarn`

**What it does:**
Captures Python warnings issued during a test.
Lets you verify your code raises the right deprecation warnings.

**When to use:**
When your code uses `warnings.warn()` or you are testing deprecated features.
Rarely needed in typical Django views.

**Usage:**
```python
import warnings

def test_deprecated_function_warns(recwarn):
    def old_function():
        warnings.warn("Use new_function() instead", DeprecationWarning)

    old_function()

    assert len(recwarn) == 1
    warning = recwarn.pop(DeprecationWarning)
    assert 'new_function' in str(warning.message)
```

---

# 💾 SECTION 12 — CACHE FIXTURE (pytest built-in)

---

## `cache`

**What it does:**
Access the pytest cache — a persistent key-value store that SURVIVES between test runs.
Unlike all other fixtures, data here is NOT cleared between tests.

**When to use:**
Advanced use cases — storing test results between runs.
For example: `pytest --lf` (last-failed) uses this cache internally.
Rarely used directly.

**Usage:**
```python
def test_store_value(cache):
    cache.set('my-plugin/my-key', [1, 2, 3], None)  # None = keep forever

def test_retrieve_value(cache):
    value = cache.get('my-plugin/my-key', default=[])
    assert value == [1, 2, 3]
```

---

# ⚙️ SECTION 13 — CONFIG FIXTURE (pytest built-in)

---

## `pytestconfig`

**What it does:**
Access the pytest configuration object — the same thing parsed from `pytest.ini`.
Lets you read command-line options and config values inside tests.

**When to use:**
Advanced — when you need to read pytest.ini values or command-line flags inside a test.

**Usage:**
```python
def test_something(pytestconfig):
    # Read verbosity level
    verbosity = pytestconfig.get_verbosity()

    # Read rootdir
    rootdir = pytestconfig.rootdir

    # Read the Django settings module we configured
    settings_module = pytestconfig.getini('DJANGO_SETTINGS_MODULE')
    assert settings_module == 'webProject.settings'
```

---

# 🎲 SECTION 14 — FAKER FIXTURE (Faker plugin)

---

## `faker` ⭐

**What it does:**
Gives you a `Faker` instance that generates realistic fake data.
Names, emails, addresses, phone numbers, dates, sentences, paragraphs — all fake but realistic.

**When to use:**
- When you need test data that looks realistic
- When you do not want to hardcode the same test data everywhere
- Creating many different users with unique data

**Usage:**
```python
def test_create_user_with_realistic_data(db, faker):
    user = User.objects.create_user(
        username=faker.user_name(),          # e.g. 'john_smith42'
        email=faker.email(),                 # e.g. 'john@example.com'
        password='StrongPass123!'            # keep password known for test login
    )
    assert User.objects.filter(username=user.username).exists()

def test_contact_form_with_fake_data(client, faker):
    response = client.post('/contact/', data={
        'name': faker.name(),               # e.g. 'Alice Johnson'
        'email': faker.email(),             # e.g. 'alice@gmail.com'
        'message': faker.paragraph()        # realistic paragraph of text
    })
    assert response.status_code == 200

# Useful faker methods:
# faker.name()            → 'John Smith'
# faker.first_name()      → 'John'
# faker.last_name()       → 'Smith'
# faker.email()           → 'john@example.com'
# faker.user_name()       → 'john_smith42'
# faker.password()        → 'xK9@mP2!'  (warning: may not meet YOUR password rules)
# faker.phone_number()    → '+1-800-555-0100'
# faker.address()         → '123 Main St, Springfield, IL'
# faker.city()            → 'Chicago'
# faker.country()         → 'United States'
# faker.sentence()        → 'The quick brown fox jumps over the lazy dog.'
# faker.paragraph()       → a full paragraph of lorem ipsum style text
# faker.date()            → '2024-03-15'
# faker.url()             → 'https://www.example.com'
# faker.uuid4()           → 'a3f4c2d1-...'
# faker.random_int(1, 100) → 42
```

---

# 🧪 SECTION 15 — SUBTESTS FIXTURE (pytest built-in)

---

## `subtests`

**What it does:**
Lets you run multiple "sub-assertions" inside a single test.
If one sub-test fails, the OTHERS still run.
Without subtests, the first `assert` failure stops the test immediately.

**When to use:**
When you want to check many things and see ALL failures at once instead of stopping at the first.

**Usage:**
```python
def test_multiple_checks(subtests):
    # Without subtests, if the first assert fails, we never see the others
    # With subtests, ALL three run and we see all failures together

    with subtests.test(msg="status code check"):
        response = client.get('/home/')
        assert response.status_code == 200

    with subtests.test(msg="template check"):
        assert 'home.html' in [t.name for t in response.templates]

    with subtests.test(msg="context check"):
        assert 'user' in response.context
```

---

# 🏠 SECTION 16 — YOUR OWN FIXTURES (from `conftest.py`)

These are the three fixtures YOU created in `webapp/tests/conftest.py`.
They are automatically available to every test in `webapp/tests/`.

---

## `test_user` ⭐ (Your fixture)

**What it does:**
Creates a regular (non-admin) User in the test database.
Already includes `db` access so you do not need to add `db` separately.

**What you get back:**
A `User` object with:
- `username = 'testuser'`
- `email = 'testuser@example.com'`
- `password = 'StrongPass123!'` (stored hashed — but you can use this plain text to log in)

**Usage:**
```python
def test_something(client, test_user):
    # test_user is a User object — already in the DB
    client.force_login(test_user)
    response = client.get('/home/')
    assert response.status_code == 200

def test_access_user_data(test_user):
    assert test_user.username == 'testuser'
    assert test_user.email == 'testuser@example.com'
    assert test_user.is_staff == False
    assert test_user.is_superuser == False
```

---

## `admin_user` ⭐ (Your fixture)

**What it does:**
Creates a superuser in the test database.
Has full admin permissions.

**What you get back:**
A `User` object with:
- `username = 'adminuser'`
- `email = 'admin@example.com'`
- `is_staff = True`
- `is_superuser = True`

**Usage:**
```python
def test_admin_only_view(client, admin_user):
    client.force_login(admin_user)
    response = client.get('/admin-dashboard/')
    assert response.status_code == 200

def test_regular_user_blocked_from_admin(client, test_user):
    client.force_login(test_user)
    response = client.get('/admin-dashboard/')
    assert response.status_code in [302, 403]  # redirected or forbidden
```

---

## `logged_in_client` ⭐ (Your fixture)

**What it does:**
Returns the `client` fixture but already logged in as `test_user`.
Combines `client` + `test_user` + `force_login` in one convenience fixture.

**When to use:**
When you are testing a view that requires `@login_required` and
you do NOT care about testing the login process itself.

**Usage:**
```python
def test_protected_home_page(logged_in_client):
    response = logged_in_client.get('/home/')
    assert response.status_code == 200  # no redirect to login

def test_audio_page_requires_login(client):
    response = client.get('/audio/')
    assert response.status_code == 302  # not logged in → redirected

def test_audio_page_loads_when_logged_in(logged_in_client):
    response = logged_in_client.get('/audio/')
    assert response.status_code == 200  # logged in → page loads
```

---

# 🔗 SECTION 17 — HOW FIXTURES CHAIN TOGETHER

Fixtures can depend on other fixtures. This is called **fixture chaining** or **composition**.

```
logged_in_client
  ↓ depends on
  ├── client          (built-in pytest-django fixture)
  └── test_user
        ↓ depends on
        └── db        (built-in pytest-django fixture)
```

When your test uses `logged_in_client`, pytest automatically:
1. Sets up `db` (database access)
2. Creates `test_user` (using `db`)
3. Sets up `client` (fake browser)
4. Calls `client.force_login(test_user)`
5. Returns the logged-in `client` to your test

You just write:
```python
def test_home(logged_in_client):
    response = logged_in_client.get('/home/')
    assert response.status_code == 200
```
And ALL of that setup happens automatically. ✅

---

# ⚡ SECTION 18 — FIXTURE SCOPE QUICK REFERENCE

| Scope | How often recreated | Use when |
|---|---|---|
| `function` (DEFAULT) | Every single test | Most tests — safest |
| `class` | Once per test class | Shared setup for a class |
| `module` | Once per file | Expensive setup shared by a whole file |
| `session` | Once for entire test run | Very expensive setup (e.g. large test DB) |

```python
@pytest.fixture(scope='function')  # default — fresh for every test
def test_user(db): ...

@pytest.fixture(scope='class')     # one user shared within each class
def shared_user(db): ...

@pytest.fixture(scope='module')    # one user shared across the whole file
def module_user(db): ...

@pytest.fixture(scope='session')   # one user for the ENTIRE test run
def session_user(django_db_setup): ...
# NOTE: session-scope fixtures need django_db_setup, not db
```

**Warning:** Higher scope = less isolation = harder to debug failures.
Always start with `function` (default). Only increase scope if tests are too slow.

---

# 🚀 SECTION 19 — FIXTURE QUICK PICK GUIDE

| You want to... | Use this fixture |
|---|---|
| Hit the database in a test | `db` |
| Use real transactions in a test | `transactional_db` |
| Make HTTP requests (GET, POST) | `client` |
| Make requests as admin | `admin_client` |
| Make requests without URL routing | `rf` |
| Create a regular test user | `test_user` (your conftest.py) |
| Create an admin test user | `admin_user` (your conftest.py) |
| Get a client already logged in | `logged_in_client` (your conftest.py) |
| Check emails were sent | `mailoutbox` |
| Test with different settings | `settings` |
| Count database queries | `django_assert_num_queries` |
| Cap database queries | `django_assert_max_num_queries` |
| Write/read temp files | `tmp_path` |
| Capture print() output | `capsys` |
| Capture log messages | `caplog` |
| Replace a function temporarily | `monkeypatch` |
| Generate realistic fake data | `faker` |
| Get the correct User model class | `django_user_model` |
| Run a real HTTP server | `live_server` |

---

# 📖 SECTION 20 — COMBINING FIXTURES IN ONE TEST

You can use as many fixtures as you need in a single test.
Just list them as parameters.

```python
def test_complex_scenario(
    client,                         # fake browser
    test_user,                      # creates a user
    mailoutbox,                     # captures emails
    settings,                       # lets us change settings
    django_assert_max_num_queries,  # checks query count
    tmp_path,                       # temp folder
    caplog,                         # captures logs
    faker,                          # fake data generator
):
    # Change a setting for this test only
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

    # Log in
    client.force_login(test_user)

    # Check page loads with max 5 queries
    with django_assert_max_num_queries(5):
        response = client.get('/home/')
    assert response.status_code == 200

    # Check no emails were sent just from loading the page
    assert len(mailoutbox) == 0

    # Create a temp file
    file = tmp_path / 'test.txt'
    file.write_text(faker.sentence())
    assert file.exists()
```

---

*Last Updated: February 2026*
*pytest version: 9.0.2 | pytest-django version: 4.12.0 | Django version: 5.2.8*
*Run `pytest --fixtures` in your terminal to see the live updated list*
