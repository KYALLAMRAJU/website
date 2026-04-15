from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from webapp.forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from webapp.models import *
from django.views.generic import (
    View,
    TemplateView,
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.urls import reverse_lazy
from django.core.mail import (
    send_mail,
)  # BadHeaderError removed in Django 7 — use ValueError instead
import time
import traceback
from django.db import connection
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from drf_spectacular.utils import extend_schema


#  Create your views here.


@require_GET
@never_cache
def health_check(request):
    """
    Health check endpoint — used by load balancers, uptime monitors, and Kubernetes probes.
    Returns 200 OK when the app and database are reachable, 503 otherwise.

    URL: /health/
    Used by: AWS ALB, Nginx upcheck, UptimeRobot, GitHub Actions smoke test
    """
    health = {
        "status": "ok",
        "db": "ok",
        "cache": "ok",
    }
    http_status = 200

    # Database check
    try:
        connection.ensure_connection()
    except Exception as e:
        health["db"] = f"error: {e}"
        health["status"] = "degraded"
        http_status = 503

    # Cache check (only when cache is configured)
    try:
        from django.core.cache import cache

        cache.set("health_check_ping", "pong", timeout=5)
        if cache.get("health_check_ping") != "pong":
            health["cache"] = "error: read-back failed"
            health["status"] = "degraded"
            http_status = 503
    except Exception as e:
        health["cache"] = f"error: {e}"
        # Cache failure is non-critical (app still works), don't set 503

    return JsonResponse(health, status=http_status)


def csrf_failure(request, reason=""):
    """Handle CSRF verification failures"""
    return render(
        request,
        "htmlfiles/csrf_error.html",
        {"message": "CSRF verification failed. Please try again.", "reason": reason},
        status=403,
    )


# ─── CUSTOM ERROR HANDLERS ────────────────────────────────────────────────────
# These replace Django's default white error pages with a proper UI error page.
# Registered in webProject/urls.py as handler404, handler500, handler403, handler400.
# NOTE: These only show when DEBUG = False in settings.py.
#       When DEBUG = True, Django shows its own detailed debug page instead.


def error_404(request, exception):
    """404 - Page Not Found: user typed a wrong URL or resource doesn't exist"""
    return render(
        request,
        "htmlfiles/error.html",
        {
            "status_code": 404,
            "message": "The page you are looking for does not exist or has been moved.",
        },
        status=404,
    )


def error_500(request):
    """500 - Server Error: something crashed on the backend"""
    return render(
        request,
        "htmlfiles/error.html",
        {"status_code": 500, "message": "Something went wrong on our end. Please try again later."},
        status=500,
    )


def error_403(request, exception):
    """403 - Forbidden: user doesn't have permission to access this page"""
    return render(
        request,
        "htmlfiles/error.html",
        {"status_code": 403, "message": "You do not have permission to access this page."},
        status=403,
    )


def error_400(request, exception):
    """400 - Bad Request: the request sent by the browser was invalid"""
    return render(
        request,
        "htmlfiles/error.html",
        {
            "status_code": 400,
            "message": "The request could not be understood. Please check the URL and try again.",
        },
        status=400,
    )


# ──────────────────────────────────────────────────────────────────────────────


"""def cookie_refresh(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        username = request.COOKIES.get('username')
        # If cookie missing, redirect to login
        if not username:
            messages.warning(request, "⚠️ Your session expired. Please log in again.")
            return redirect('/loginpage/')
        # Call the original view
        response = view_func(request, *args, **kwargs)
        # 🟢 Refresh cookie rolling expiry (2 minutes = 120 sec)
        response.set_cookie(
            key='username',
            value=username,
            max_age=120,  # <--- Rolling expiry refreshed on each visit
            httponly=False,
            secure=False,
            samesite='Lax'
        )
        print("🔁 Cookie refreshed for:", username)
        print("Current Cookies:", request.COOKIES)
        print("Response Cookies:", response.cookies)
        return response  # <-- VERY IMPORTANT
    return wrapper"""


def signupForm_view(request):
    form = signupForm()  # creating an object of signupForm class which is of empty form
    submitted = False
    if request.method == "POST":
        form = signupForm(request.POST)
        if form.is_valid():
            print(
                "All validations passed and signup form is valid please check forms.py for validation rules"
            )
            print("Raw POST data:", request.POST)
            print("Cleaned data:", form.cleaned_data, type(form.cleaned_data))
            # Access individual fields using cleaned_data dictionary
            username = form.cleaned_data["username"]
            firstname = form.cleaned_data["first_name"]
            lastname = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            print("Username:", username)
            print("First Name:", firstname)
            print("Last Name:", lastname)
            print("Email:", email)
            # saving the form data into auth user table
            user = form.save()
            user.set_password(password)  # Hashing the password before saving
            user.save()
            submitted = True
            print("✅ Signup successful for:", username)

            # ========== EMAIL VERIFICATION FOR SIGNUP ==========
            try:
                subject = "Welcome to Advaitam - Verify Your Email"  # change this line according to your company
                message = f"""
Hello {firstname.capitalize()} {lastname.capitalize()},

Thank you for signing up on Advaitam!  # change this line according to your company

Your account has been created successfully with the following details:
- Username: {username}
- Email: {email}

This email confirms that your email address is registered with us. You can now log in with your credentials.

Please keep your password safe and do not share it with anyone.

If you did not create this account, please contact us immediately.

Best regards,
Advaitam Team  # change this line according to your company
"""
                # Send verification email
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                print("❌ Email sending failed during signup:", e)
                messages.warning(
                    request, f"Account created but email could not be sent. You can still login."
                )

            # Add a success message or redirect to another page after successful signup
            messages.success(
                request,
                f"Account created successfully for {firstname.capitalize()}!. Verification email sent to {email}. Please login to continue.",  # change this line according to your company
            )
            # Redirect to login page after successful signup
            return redirect(
                "/loginpage/"
            )  # change this line according to your company (update to your login URL)
        else:
            print("❌ Signup form is invalid")
            print(form.errors)  # printing error messages if form is invalid
            pass  # form errors are rendered back to the template automatically
    return render(request, "htmlfiles/signupform.html", {"form": form, "submitted": submitted})


""" -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""


def forgotpasswordForm_view(request):
    form = resetpasswordForm()  # creating an object of LoginForm class which is of empty form
    submitted = False
    if request.method == "POST":
        form = resetpasswordForm(
            request.POST
        )  # creating an object of LoginForm class which is of filled form if request is POST with end user data
        if form.is_valid():
            # Access individual fields using cleaned_data dictionary
            email = form.cleaned_data["email"]
            newpassword = form.cleaned_data["newpassword"]
            confirmpassword = form.cleaned_data["confirmpassword"]
            print(
                "All validations passed and forgot password form is valid please check forms.py for validation rules"
            )
            print("Email:", email)
            print("New Password:", newpassword)
            print("Confirm Password:", confirmpassword)
            user = User.objects.get(email=email)
            user.set_password(newpassword)
            user.save()
            print("✅ Password reset successful for:", email)

            # ========== EMAIL NOTIFICATION FOR PASSWORD RESET ==========
            try:
                subject = "Advaitam - Password Reset Successful"  # change this line according to your company
                message = f"""
                            Hello {user.first_name.capitalize() if user.first_name else user.username},
                            
                            Your password has been successfully reset.
                            
                            Account Email: {email}
                            
                            You can now log in with your new password. Please keep your password safe and do not share it with anyone.
                            
                            If you did not request this password reset, please contact us immediately.
                            
                            Best regards,
                            Advaitam Team  # change this line according to your company
                            """
                # Send password reset confirmation email
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                print("❌ Email sending failed during password reset:", e)
                messages.warning(
                    request, f"Password reset successful but confirmation email could not be sent."
                )

            # Add a success message or redirect to another page after successful password reset
            messages.success(
                request,
                f"Password reset successfully for {email.split('@')[0].capitalize()}. Confirmation email sent to {email}. Please login with your new password to continue.",  # change this line according to your company
            )
            # Redirect to login page after successful password reset
            return redirect(
                "/loginpage/"
            )  # change this line according to your company (update to your login URL)
        else:
            print("❌ Forgot password form is invalid")
            print(form.errors)  # printing error messages if form is invalid
            pass  # form errors are rendered back to the template automatically
    return render(request, "htmlfiles/forgotpassword.html", {"form": form})


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# LOGIN FORM WITHOUT USING COOKIES OR SESSIONS MANAGEMENT CONCEPT
# def loginForm_view(request):
#     form = loginForm()  # creating an object of LoginForm class which is of empty form if request is GET
#     submitted = False
#     if request.method == 'POST':
#         form = loginForm(request.POST)  # creating an object of LoginForm class which is of filled form if request is POST with end user data
#         if form.is_valid():
#             form.save(commit=True)
#             print("All validations passed and form is valid please check forms.py for validation rules")
#             # You can also access the raw POST data if needed
#             print("Raw POST data:", request.POST)
#             print("Cleaned data:", form.cleaned_data, type(form.cleaned_data))
#             # Access individual fields using cleaned_data dictionary
#             email = form.cleaned_data['loginemail']
#             password = form.cleaned_data['loginpassword']
#             print("Email:", email)
#             print("Password:", password)
#             submitted = True
#             # Add a success message or redirect to another page after successful login
#             messages.success(request, f"Welcome , {email.split('@')[0].capitalize()}!")
#             # Redirect to home page after successful login
#             return redirect('/home/')
#         else:
#             print("Form is invalid")
#             print(form.errors)  # printing error messages if form is invalid
#     return render(request, 'htmlfiles/login.html', {'form': form, 'submitted': submitted})
#
#
# LOGIN FORM USING COOKIES CONCEPT
#
# def loginForm_view(request):
#     form = loginForm()  # creating an object of LoginForm class which is of empty form if request is GET
#     submitted = False
#     if request.method == 'POST':
#         form = loginForm(
#             request.POST)  # creating an object of LoginForm class which is of filled form if request is POST with end user data
#         email = request.POST.get('loginemail')
#         password = request.POST.get('loginpassword')
#         if form.is_valid():
#             print("Cleaned data:", form.cleaned_data, type(form.cleaned_data))
#             username = email.split('@')[0].upper()
#             response = redirect('/home/')
#             response.set_cookie('username', username, max_age=120)
#             print(response.cookies)
#             messages.success(request, f"Welcome , {username}!")
#             print("✅ Login successful for:", username)
#             return response
#         else:
#             messages.error(request,
#                            " Invalid login credentials. Please try again.If you don't have an account, please sign up using signup link at bottom.")
#             print("❌ Invalid login for email:", email)
#             return render(request, 'htmlfiles/login.html', {'form': form, 'submitted': submitted})
#     else:
#         print("Form is invalid")
#         print(form.errors)  # printing error messages if form is invalid
#     return render(request, 'htmlfiles/login.html', {'form': form, 'submitted': submitted})
#
#
# LOGIN FORM USING SESSIONS MANAGEMENT CONCEPT

# def loginForm_view(request):
#     form = loginForm()  # creating an object of LoginForm class which is of empty form if request is GET
#     submitted = False
#     if request.method == 'POST':
#         form = loginForm(request.POST)  # creating an object of LoginForm class which is of filled form if request is POST with end user data
#         if form.is_valid():
#             print("All validations passed and form is valid please check forms.py for validation rules")
#             # You can also access the raw POST data if needed
#             print("Raw POST data:", request.POST)
#             print("Cleaned data:", form.cleaned_data, type(form.cleaned_data))
#             email = form.cleaned_data['loginemail']
#             password = form.cleaned_data['loginpassword']
#             print("Email:", email)
#             print("Password:", password)
#             submitted = True
#             username = email.split('@')[0].upper()
#             request.session['username'] = username # Storing username in session
#             print("session data:",request.session.items())
#             print("session expiry time (in seconds):",request.session.get_expiry_age())
#             print("session expiry date:",request.session.get_expiry_date())
#             messages.success(request, f"Welcome , {username}!")
#             return redirect('/home/')
#         else:
#             print("Form is invalid")
#             print(form.errors)  # printing error messages if form is invalid
#     return render(request, 'htmlfiles/login.html', {'form': form, 'submitted': submitted})


# login form using django built-in authentication system
def loginForm_view(request):
    form = loginForm()
    submitted = False
    if request.method == "POST":
        form = loginForm(request.POST)
        if form.is_valid():
            print(
                "All validations passed and login form is valid please check forms.py for validation rules"
            )
            print("Raw POST data:", request.POST)
            print("Cleaned data:", form.cleaned_data, type(form.cleaned_data))
            email = form.cleaned_data["loginemail"]
            password = form.cleaned_data["loginpassword"]
            print("Email:", email)
            print("Password:", password)
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
                print("Username found:", username)
            except User.DoesNotExist:
                username = None
                print("❌ User not found for email:", email)
                messages.error(
                    request,
                    "User not found ! Please check your entered data once again or sign up using signup link at bottom.",
                )
                return render(request, "htmlfiles/login.html", {"form": form})
            # ✅ Try login
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print("✅ Login successful for:", username)
                messages.success(
                    request, f"Welcome , {username}!"
                )  # change this line according to your company (customize welcome message)
                return redirect(
                    request.GET.get("next", "/home/")
                )  # change this line according to your company (update post-login redirect URL)
            else:
                print(
                    "❌ Authentication failed for:",
                    username,
                    "(wrong password or inactive account)",
                )
                messages.error(
                    request,
                    "Password is wrong or account is inactive.If you don't have an account, please sign up using signup link at bottom.",
                )
        else:
            print("❌ Login form is invalid")
            print(form.errors)  # printing error messages if form is invalid
    return render(request, "htmlfiles/login.html", {"form": form})


# ============================================================
# SESSION PING — keeps session alive when user clicks "Stay Logged In"
# ============================================================


@login_required
def session_ping(request):
    """Silently refreshes the session expiry timer."""
    if request.method == "POST":
        request.session.modified = True  # Django will save & reset the cookie age
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "error", "message": "POST required"}, status=405)


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required
def homepage_view(request):  # Accessing username from session
    print("✅ Homepage accessed by user:", request.user.username)
    return render(request, "htmlfiles/home.html")


@login_required
def aboutpage_view(request):
    about_list = aboutdetails.objects.all()
    first = about_list[0]
    second = about_list[1]
    third = about_list[2]
    fourth = about_list[3]
    return render(
        request,
        "htmlfiles/about.html",
        {
            "about_list": about_list,
            "first": first,
            "second": second,
            "third": third,
            "fourth": fourth,
        },
    )


@login_required
def aboutdetail_view(request, title):
    about_detail = get_object_or_404(
        aboutdetails, slug=title
    )  # to get record matched with the slug title
    return render(request, "htmlfiles/aboutdetail.html", {"about_detail": about_detail})


@login_required
def audiopage_view(request):
    # print(10/0)  # this line is for testing purpose to check if middleware is working for exception handling
    return render(request, "htmlfiles/audio.html")


@login_required
def gallery_view(request):
    return render(request, "htmlfiles/gallery.html")


@login_required
def books_view(request):
    return render(request, "htmlfiles/books.html")


@login_required
def contact_view(request):
    if request.method == "POST":
        form = contactusForm(request.POST)
        if form.is_valid():
            name = (
                f"{request.user.first_name} {request.user.last_name}".strip().upper()
                or request.user.username.upper()
            )
            email = request.user.email
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]
            contacus.objects.create(name=name, email=email, subject=subject, message=message)
            try:
                admin_email = settings.ADMIN_EMAIL
                user_email = email.strip() if email else None

                # ── Email 1: Notify admin ──────────────────────────────────────
                admin_subject = f"[Advaitam Contact] {subject} - from {name}"  # change this line according to your company
                admin_body = (
                    f"You have received a new contact message from:\n\n"
                    f"Name   : {name}\n"
                    f"Email  : {user_email or 'Not provided'}\n"
                    f"Subject: {subject}\n\n"
                    f"Message:\n{message}"
                )
                send_mail(
                    admin_subject,
                    admin_body,
                    settings.DEFAULT_FROM_EMAIL,
                    [admin_email],
                    fail_silently=False,
                )

                # ── Email 2: Confirmation to user (only if different from admin) ──
                if user_email and user_email.lower() != admin_email.lower():
                    time.sleep(1.5)  # Mailtrap free plan: max 1 email/second
                    user_subject = "Advaitam - We received your message!"  # change this line according to your company
                    user_body = (
                        f"Dear {name.title()},\n\n"
                        f"Thank you for reaching out to us. We have received your message "  # change this line according to your company
                        f'regarding "{subject}" and will get back to you soon.\n\n'
                        f"Your message:\n{message}\n\n"
                        f"Best regards,\nAdvaitam Team"  # change this line according to your company
                    )
                    send_mail(
                        user_subject,
                        user_body,
                        settings.DEFAULT_FROM_EMAIL,
                        [user_email],
                        fail_silently=False,
                    )
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Your request has been noted. We will get back to you soon!",
                    }
                )
            except Exception as e:
                traceback.print_exc()
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "There was an error sending your message. Please try again later.",
                    },
                    status=500,
                )
        else:
            return JsonResponse(
                {"status": "error", "message": "Please fill in all required fields correctly."},
                status=400,
            )
    return redirect(request.META.get("HTTP_REFERER", "/"))


# ----------------------------------------------THE BELOW ONES ARE FOR MY PRACTICE.[CRUD USING FUNCTION BASED VIEWS] USING FUNCTION BASED VIEWS-------------------------------------------------

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def wish_retrieveview(request):
    print(request.COOKIES)
    # count = int(request.COOKIES.get('count', 0))
    # count += 1
    wish_list = wishdata.objects.all()  # To get list of all the data in the table
    # wish_list = wishdata.objects.filter(name__startswith='A')  # Django ORM code to fetch all records from wishdata table whose name starts with A
    # wish_list = wishdata.objects.all().values_list("id", "name", "astrology_message")
    print(wish_list)
    paginator = Paginator(
        wish_list, 8
    )  # 10 records per page #create an object of paginator class with what data u want to use for pagination and how many records per page
    page_number = request.GET.get(
        "page"
    )  # getting the current page number from url query parameter which we passed from pagination.html file next and previous links
    try:
        wish_list = paginator.page(
            page_number
        )  # getting the records of that particular page number
    except PageNotAnInteger:
        wish_list = paginator.page(
            1
        )  # getting the first page records if page number is not an integer or if we provide direct url without page number like 127.0.0.1:8000
    except EmptyPage:
        wish_list = paginator.page(
            paginator.num_pages
        )  # getting the last page records if page number is out of range like if total pages are 10 and we give page number as 100
    response = render(request, "htmlfiles/wish.html", {"wish_list": wish_list})
    # response.set_cookie('count', count)
    return response


def wish_insertview(request):
    form = wishForm()
    if request.method == "POST":
        form = wishForm(request.POST)
        if form.is_valid():
            print("Wish form is valid, saving data to database")
            print("Cleaned data:", form.cleaned_data)
            form.save()
            print("✅ Wish data saved successfully")
            return redirect("/wish/")
        else:
            print("❌ Wish form is invalid")
            print(form.errors)
    return render(request, "htmlfiles/wishinsert.html", {"form": form})


def wish_updateview(request, id):
    wish = wishdata.objects.get(id=id)  # to get record matched with the id
    print("Fetched wish data for update:", wish.id, wish.name)
    form = wishForm(instance=wish)
    if request.method == "POST":
        form = wishForm(request.POST, instance=wish)
        if form.is_valid():
            print("Wish update form is valid, saving updated data to database")
            print("Updated cleaned data:", form.cleaned_data)
            form.save()
            print("✅ Wish data updated successfully for id:", id)
            return redirect("/wish/")
        else:
            print("❌ Wish update form is invalid")
            print(form.errors)
    return render(request, "htmlfiles/wishupdate.html", {"form": form})


def wish_deleteview(request, id):
    wish = wishdata.objects.get(id=id)  # to get record matched wish data with the id
    print("Deleting wish data for id:", id, "Name:", wish.name)
    wish.delete()
    print("✅ Wish data deleted successfully for id:", id)
    return redirect("/wish/")


# ------------------------------------------------THE BELOW ONES ARE FOR MY PRACTICE.[CLASS BASED VIEWS ]-------------------------------------------------------------
class Helloworldview(View):
    def get(self, request):
        return HttpResponse(
            "Hello World! This is my first class based view in Django."
        )  # there is no template file associated with this view just returning a simple http response


# THE BELOW ONE IS A NORMAL VIEW CLASS BASED VIEW FOR RETRIEVING WISH DATA
class Wishgetview(View):
    def get(self, request):
        wish_list = wishdata.objects.all()
        return render(request, "htmlfiles/wish.html", {"wish_list": wish_list})


# THE BELOW ONE IS A TEMPLATE VIEW CLASS BASED VIEW FOR RETRIEVING WISH DATA
class wishgetviewtemplateview(TemplateView):
    template_name = "htmlfiles/wish.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            **kwargs
        )  # getting context object from parent class amd it is a dictionary
        context["wish_list"] = (
            wishdata.objects.all()
        )  # adding wish_list to context and overriding the get_context_data method with our own data
        return context

    # ---------------------CRUD OPERATIONS USING CLASS BASED VIEWS: USE IF WE NEED TO PERFORM DB OPERATIONS------------------------------------------------


class wishcreateview(CreateView):
    model = wishdata
    fields = "__all__"  # to include all fields from the model in the form
    # default template name is 'webapp/wishdata_form.html'
    # create will always call get_absolute_url method of the model to redirect to detail view of the created object


class wishupdateview(UpdateView):
    model = wishdata
    fields = "__all__"  # to include all fields from the model in the form
    # default template name is 'webapp/wishdata_form.html'


class wishdeleteview(DeleteView):
    model = wishdata
    # success_url = '/wishlistcbv2/'  # URL to redirect after successful deletion
    # default template name is 'webapp/wishdata_confirm_delete.html'
    success_url = reverse_lazy("wishlistcbv2")  # using reverse_lazy to avoid circular import issues


class wishlistview(ListView):
    model = wishdata
    # the below are optional attributes which are defaulted by django if not provided
    # template_name = 'wishdata_list.html'  # Default is '<app_label>/<model_name>_list.html'
    # the below are optional methods which can be overridden to customize the behavior
    # template_name = 'htmlfiles/wish.html'  # this is our custom template name
    # the below are optional attributes which are defaulted by django if not provided
    # context_object_name = 'wishdata_list'  # Default is '<model_name>_list'
    # the below are optional methods which can be overridden to customize the behavior
    context_object_name = "wish"
    paginate_by = 20  # Number of items per page


class wishlistview2(ListView):
    model = wishdata
    template_name = "webapp/wishlistindex.html"
    context_object_name = "wish2"


class wishdetailview(DetailView):
    model = wishdata
    # default template name is 'webapp/wishdata_detail.html'
    # default context object: wishdata(modelclassname) or object
