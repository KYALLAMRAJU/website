# =============================================================================
# PYTEST LEARNING FILE — loginForm_view
# =============================================================================
#
# VIEW BEING TESTED:  webapp/views.py → loginForm_view()
# URL:                /loginpage/
#
# What loginForm_view does:
#   GET  request → shows the login page (empty form)
#   POST request (wrong data)  → shows errors, stays on login page
#   POST request (correct data) → logs user in, redirects to /home/
#   POST request (wrong password) → shows error message
#   POST request (user not found) → shows error message
#
# HOW TO RUN ALL TESTS:
#   pytest webapp/tests/test_login_view.py -v
#
# HOW TO RUN ONE SPECIFIC TEST:
#   pytest webapp/tests/test_login_view.py::TestLoginGET::test_login_page_loads -v
#
# =============================================================================

import pytest
import logging
from django.contrib.auth.models import User
from django.urls import reverse

logger = logging.getLogger(__name__)


# =============================================================================
# STEP 1 — WHAT IS A FIXTURE?
# =============================================================================
#
# A fixture is a HELPER that sets up data your tests need.
# Think of it like a "before each test, do this preparation".
#
# @pytest.fixture  ← this decorator tells pytest "this is a fixture"
# def my_fixture():
#     return something_useful
#
# Then in your test function, just put the fixture name as a parameter
# and pytest automatically passes it in for you.
#
# EXAMPLE BELOW:
#   - `client`      → built-in pytest-django fixture: a fake browser to make requests
#   - `db`          → built-in pytest-django fixture: gives access to the test database
#   - `test_user`   → OUR custom fixture: creates a real User in the test DB
# =============================================================================


@pytest.fixture
def test_user(db):
    """
    Creates a real User in the test database.

    WHY db?
      pytest-django by default does NOT allow database access in tests
      (to keep tests fast). Adding `db` as a parameter explicitly says
      "yes, this fixture needs DB access".

    The test database is:
      - Created fresh before tests run
      - Wiped clean after tests finish
      - NEVER touches your real db.sqlite3 or PostgreSQL
    """
    user = User.objects.create_user(
        username="testuser", email="testuser@example.com", password="StrongPass123!"
    )
    return user  # return the user so tests can use it


# =============================================================================
# STEP 2 — YOUR FIRST TEST (GET Request)
# =============================================================================
#
# ANATOMY OF A TEST:
#
#   @pytest.mark.django_db          ← allows this test to use the database
#   def test_something(client):     ← `client` is the fake browser fixture
#       response = client.get(...)  ← make a request
#       assert response.status_code == 200  ← check the result
#
# WHAT IS `assert`?
#   assert <condition>
#   If condition is True  → test PASSES ✅
#   If condition is False → test FAILS  ❌ with a clear error message
#
# WHAT IS `client`?
#   A fake browser provided by pytest-django.
#   client.get('/some/url/')   → simulates typing a URL in the browser
#   client.post('/some/url/', data={...}) → simulates submitting a form
# =============================================================================


class TestLoginGET:
    """
    GROUP 1: Testing the GET request (just loading the login page)

    CLASS-BASED GROUPING:
      We group related tests inside a class.
      class TestLoginGET  → all tests about GET requests
      class TestLoginPOST → all tests about POST requests
      This keeps things organised as your test file grows.
    """

    def test_login_page_loads(self, client):
        """
        SIMPLEST TEST POSSIBLE.

        Does the login page load at all?
        Expected: HTTP 200 OK (page loaded successfully)

        HTTP STATUS CODES you'll see often:
          200 → OK, page loaded
          302 → Redirect (e.g. after login success)
          403 → Forbidden (not logged in / CSRF fail)
          404 → Not found
        """
        url = reverse("loginpage")  # reverse() converts URL name → actual path
        # reverse('loginpage') returns '/loginpage/'
        # Using reverse() is BETTER than hardcoding '/loginpage/' because
        # if you ever change the URL in urls.py, the test still works.

        response = client.get(url)

        assert response.status_code == 200

        logger.info("Login page loaded successfully with status code 200.")

    def test_login_page_uses_correct_template(self, client):
        """
        Does the login page use the right HTML template?

        WHY TEST THIS?
          If someone accidentally changes the template name in views.py,
          this test catches it immediately.

        assertTemplateUsed() checks which template Django rendered.
        """
        url = reverse("loginpage")

        response = client.get(url)
        print(response)  # Print the response object to see its attributes (for debugging)
        assert response.status_code == 200
        # Check the correct template was used
        assert "htmlfiles/login.html" in [t.name for t in response.templates if t.name is not None]

        logging.info("the correct template is used for login page is login.html")

    def test_login_page_has_form(self, client):
        """
        Does the response contain the login form?

        response.context is the data Django passed to the template.
        In views.py: return render(request, 'login.html', {'form': form})
        So context['form'] should exist.

        WHY TEST THIS?
          If someone removes 'form' from the render() call, the template
          would crash or show a blank form. This catches that.
        """
        url = reverse("loginpage")
        response = client.get(url)

        assert "form" in response.context  # form was passed to template


# =============================================================================
# STEP 3 — TESTING POST REQUESTS
# =============================================================================
#
# POST requests are more interesting — they actually DO something.
# The login form has several possible outcomes:
#   1. Empty/invalid data submitted    → stay on page, show form errors
#   2. Wrong email (user doesn't exist) → error message
#   3. Right email, wrong password     → error message
#   4. Right email, right password     → redirect to /home/
# =============================================================================


class TestLoginPOST:
    """GROUP 2: Testing POST requests to the login form."""

    def test_empty_form_submission_stays_on_login_page(self, client):
        """
        What happens if user clicks Login with empty fields?

        Expected: stay on the login page (200), show form errors.
        Should NOT redirect (302).
        """
        url = reverse("loginpage")
        response = client.post(url, data={"loginemail": "", "loginpassword": ""})

        assert response.status_code == 200  # stayed on same page, not redirected

    def test_login_with_nonexistent_email_shows_error(self, client, db):
        """
        What if the email doesn't exist in the database at all?

        IMPORTANT LESSON:
          The form's clean() method validates the email FORMAT first.
          So we must send a valid-format email + strong password,
          otherwise the form fails validation before the view even
          tries to look up the user in the database.

          This is a great example of WHY tests are valuable — they
          force you to understand the full flow of your code.

        Expected:
          - Stay on login page (200)
          - Show an error message to the user
        """
        url = reverse("loginpage")
        response = client.post(
            url,
            data={
                "loginemail": "nobody@example.com",  # valid format, but user doesn't exist
                "loginpassword": "StrongPass123!",  # valid format password
            },
        )

        assert response.status_code == 200

        # Check an error message was shown via Django messages framework
        messages_list = list(response.wsgi_request._messages)
        assert len(messages_list) > 0

        message_texts = [str(m) for m in messages_list]
        assert any("not found" in text.lower() or "check" in text.lower() for text in message_texts)

    def test_login_with_wrong_password_shows_error(self, client, test_user):
        """
        What if email is correct but password is wrong?

        NOTE: we use `test_user` fixture here — it creates the user
        in the DB first so the email lookup succeeds, but we post
        a different password.

        Expected: stay on login page, show error message.

        HOW FIXTURES WORK WITH TESTS:
          Just put the fixture name as a parameter → pytest injects it.
          test_user fixture runs BEFORE this test, creating the user.
        """
        url = reverse("loginpage")
        response = client.post(
            url,
            data={
                "loginemail": "testuser@example.com",  # correct email (user exists)
                "loginpassword": "WrongPassword999!",  # WRONG password
            },
        )

        assert response.status_code == 200  # stayed on login page

        messages_list = list(response.wsgi_request._messages)
        message_texts = [str(m) for m in messages_list]
        assert any(
            "wrong" in text.lower() or "password" in text.lower() or "inactive" in text.lower()
            for text in message_texts
        )

    def test_successful_login_redirects_to_home(self, client, test_user):
        """
        THE HAPPY PATH — correct email + correct password.

        Expected:
          - HTTP 302 (redirect)
          - Redirects to /home/

        WHAT IS A REDIRECT?
          When login succeeds, views.py does: return redirect('/home/')
          Django returns HTTP 302 with a Location header pointing to /home/.
          The browser then automatically follows it.

        HOW TO CHECK REDIRECTS:
          response.status_code == 302  → a redirect happened
          response['Location']         → where it redirected to
          client.get(url, follow=True) → follow the redirect automatically
        """
        url = reverse("loginpage")
        response = client.post(
            url, data={"loginemail": "testuser@example.com", "loginpassword": "StrongPass123!"}
        )

        # Should redirect (302) after successful login
        assert response.status_code == 302
        # Should redirect to /home/
        assert response["Location"] == "/home/"

    def test_successful_login_user_is_authenticated(self, client, test_user):
        """
        After login, is the user actually authenticated (logged in)?

        We use follow=True to follow the redirect to /home/
        Then check response.wsgi_request.user.is_authenticated

        WHY TEST THIS?
          The redirect alone doesn't prove authentication worked.
          Maybe the view redirected but forgot to call login().
          This test catches that.
        """
        url = reverse("loginpage")
        response = client.post(
            url,
            data={"loginemail": "testuser@example.com", "loginpassword": "StrongPass123!"},
            follow=True,
        )  # follow=True automatically follows the redirect

        # After following redirect, check the user is authenticated
        assert response.wsgi_request.user.is_authenticated
        assert response.wsgi_request.user.username == "testuser"


# =============================================================================
# STEP 4 — TESTING REDIRECTS FOR LOGGED-IN USERS
# =============================================================================
#
# loginForm_view doesn't explicitly redirect logged-in users,
# but @login_required views like /home/ do.
# Let's test that behaviour too.
# =============================================================================


class TestLoginRedirectBehaviour:
    """GROUP 3: Testing redirect behaviour."""

    def test_unauthenticated_user_cannot_access_home(self, client):
        """
        If a user is NOT logged in and tries to go to /home/,
        they should be redirected to the login page.

        This tests that @login_required decorator on homepage_view works.
        """
        response = client.get("/home/")

        # Should redirect to login page
        assert response.status_code == 302
        assert "/loginpage/" in response["Location"]

    def test_login_with_next_param_redirects_correctly(self, client, test_user):
        """
        ADVANCED: The `?next=` URL parameter.

        When Django redirects an unauthenticated user to login,
        it adds ?next=/original/url/ to the login URL.
        After login, views.py does: redirect(request.GET.get('next', '/home/'))
        So the user ends up at the page they originally wanted.

        Example:
          User tries to visit /audio/
          → Redirected to /loginpage/?next=/audio/
          → After login → redirected back to /audio/
        """
        url = reverse("loginpage") + "?next=/audio/"
        response = client.post(
            url, data={"loginemail": "testuser@example.com", "loginpassword": "StrongPass123!"}
        )

        assert response.status_code == 302
        assert response["Location"] == "/audio/"  # went to the originally requested page


# =============================================================================
# STEP 5 — PARAMETRIZE (testing many inputs with one test)
# =============================================================================
#
# WHAT IS @pytest.mark.parametrize?
#   Instead of writing 5 separate tests with slightly different data,
#   you write ONE test and give it multiple sets of inputs.
#   pytest runs it once for each set.
#
# SYNTAX:
#   @pytest.mark.parametrize('param1, param2', [
#       ('value1a', 'value2a'),   ← run 1
#       ('value1b', 'value2b'),   ← run 2
#   ])
#   def test_something(self, client, param1, param2):
#       ...
# =============================================================================


class TestLoginInvalidInputs:
    """GROUP 4: Testing many invalid inputs using parametrize."""

    @pytest.mark.parametrize(
        "email, password",
        [
            ("", ""),  # both empty
            ("notanemail", "somepassword"),  # invalid email format
            ("a" * 200 + "@x.com", "password"),  # email too long
            ("test@example.com", ""),  # password empty
        ],
    )
    def test_invalid_form_data_stays_on_login_page(self, client, email, password):
        """
        For ALL these invalid inputs, the page should NOT redirect.
        It should stay on the login page (200).

        Instead of 4 separate test functions, we have ONE test
        that runs 4 times with different data.

        In the output you'll see:
          PASSED test_login_view.py::TestLoginInvalidInputs::test_invalid_...[ -  ]
          PASSED test_login_view.py::TestLoginInvalidInputs::test_invalid_...[notanemail-somepassword]
          etc.
        """
        url = reverse("loginpage")
        response = client.post(url, data={"loginemail": email, "loginpassword": password})

        # All invalid inputs should stay on the form page, not redirect
        assert response.status_code == 200


# =============================================================================
# STEP 6 — USING conftest.py (shared fixtures across files)
# =============================================================================
#
# Right now our `test_user` fixture is only available in THIS file.
# If you have 10 test files and all need a test user, you'd have to
# copy the fixture into each file — messy!
#
# SOLUTION: conftest.py
#   Put shared fixtures in webapp/tests/conftest.py
#   pytest automatically finds and loads them for ALL test files.
#
# We'll create that file next (see conftest.py in this folder).
# =============================================================================


# =============================================================================
# STEP 7 — MOCKING (faking external calls)
# =============================================================================
#
# WHAT IS MOCKING?
#   Some code calls external services (email, AWS, Claude AI, etc.)
#   In tests, you don't want to actually send emails or make API calls.
#   Mocking replaces the real function with a fake one that you control.
#
# HOW:
#   from unittest.mock import patch
#
#   @patch('django.core.mail.send_mail')   ← replace send_mail with a fake
#   def test_something(self, mock_send_mail, client, test_user):
#       mock_send_mail.return_value = 1    ← fake it returns success
#       ...
#       assert mock_send_mail.called       ← verify it WAS called
#
# The login view doesn't call email directly, but signupForm_view does.
# We'll add mock tests for signup in the next test file.
# =============================================================================


class TestLoginMocking:
    """GROUP 5: Demonstrating mocking concept on login."""

    def test_login_calls_authenticate(self, client, test_user):
        """
        We can mock django.contrib.auth.authenticate to verify
        the view actually calls it with the right arguments.

        from unittest.mock import patch

        @patch('webapp.views.authenticate')  ← patch it where it's USED
        def test_...(self, mock_auth, client, test_user):
            mock_auth.return_value = test_user  ← fake: return our user
            response = client.post(url, data={...})
            mock_auth.assert_called_once()  ← verify authenticate was called

        For now, we test indirectly — if login works, authenticate was called.
        """
        url = reverse("loginpage")
        response = client.post(
            url, data={"loginemail": "testuser@example.com", "loginpassword": "StrongPass123!"}
        )
        # If authenticate() wasn't called, login wouldn't work
        # So a 302 redirect proves it was called successfully
        assert response.status_code == 302
