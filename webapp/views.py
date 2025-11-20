from django.core import paginator
from django.shortcuts import render, redirect,get_object_or_404
from webapp.forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from webapp.models import *
from django.views.generic import View,TemplateView,ListView,DetailView,CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMultiAlternatives,send_mail,EmailMessage,send_mass_mail
from datetime import datetime, timedelta
import random as r
from django.utils import timezone
import requests
import pytz
from django.conf import settings

                                                                #  Create your views here.

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
    if request.method == 'POST':
        form = signupForm(request.POST)
        if form.is_valid():
            print("All validations passed and form is valid please check forms.py for validation rules")
            # You can also access the raw POST data if needed
            print("Raw POST data:", request.POST)
            print("Cleaned data:", form.cleaned_data, type(form.cleaned_data))
            # Access individual fields using cleaned_data dictionary
            username= form.cleaned_data['username']
            firstname = form.cleaned_data['first_name']
            lastname = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            print("Username:", username)
            print("Name:", firstname+' '+lastname)
            print("Email:", email)
            print("Password:", password)
            # saving the form data into auth user table
            user=form.save()
            user.set_password(password)  # Hashing the password before saving
            user.save()
            submitted = True
            # Add a success message or redirect to another page after successful signup
            messages.success(request,f"Account created successfully for {firstname.capitalize()}!. Please login to continue.")
            # Redirect to login page after successful signup
            return redirect('/loginpage/')
        else:
            print("Form is invalid")
            print(form.errors)  # printing error messages if form is invalid
    return render(request, 'htmlfiles/signupform.html', {'form': form, 'submitted': submitted})


""" -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""


def forgotpasswordForm_view(request):
    form = resetpasswordForm()  # creating an object of LoginForm class which is of empty form
    submitted = False
    if request.method == 'POST':
        form = resetpasswordForm(request.POST)  # creating an object of LoginForm class which is of filled form if request is POST with end user data
        if form.is_valid():
            print("Password Reset successful please login with new password")
            print("All validations passed and form is valid please check forms.py for validation rules")
            # You can also access the raw POST data if needed
            print("Raw POST data:", request.POST)
            print("Cleaned data:", form.cleaned_data, type(form.cleaned_data))
            # Access individual fields using cleaned_data dictionary
            email = form.cleaned_data['email']
            newpassword = form.cleaned_data['newpassword']
            confirmpassword = form.cleaned_data['confirmpassword']
            print("Email:", email)
            print("New Password:", newpassword)
            print("Confirm New Password:", confirmpassword)
            user=User.objects.get(email=email)
            user.set_password(newpassword)
            user.save()
            # Add a success message or redirect to another page after successful password reset
            messages.success(request,f"Password reset successfully for {email.split('@')[0].capitalize()}. Please login with your new password to continue.")
            # Redirect to login page after successful password reset
            return redirect('/loginpage/')
        else:
            print("Form is invalid")
            print(form.errors)  # printing error messages if form is invalid
    return render(request, 'htmlfiles/forgotpassword.html', {'form': form})


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
    print("THIS LINE IS FOR DEBUGGING PURPOSE ONLY: CURRENT : CHECKING IF IT IS HITTING THE MIDDLEWARE AND VIEW FUNCTION")
    submitted = False
    if request.method == 'POST':
        form = loginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['loginemail']
            password = form.cleaned_data['loginpassword']
            try:
                user_obj = User.objects.get(email=email)
                username = user_obj.username
            except User.DoesNotExist:
                username = None
                messages.error(request, "User not found:Please check your entered data once again or sign up using signup link at bottom.")
                return render(request, 'htmlfiles/login.html', {'form': form})
            print("DEBUG EMAIL:", email)
            print("DEBUG PASSWORD:", password)
            print("DEBUG USERNAME:", username)
            print("DEBUG STORED HASH:", user_obj.password)
            print("CHECK PASSWORD MATCH:", user_obj.check_password(password))
            print("IS ACTIVE:", user_obj.is_active)
            # ✅ Try login
            user = authenticate(request, username=username, password=password)
            print("AUTHENTICATE RESULT:", user)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome , {username}!")
                return redirect(request.GET.get('next', '/home/'))
            else:
                messages.error(request, "Password is wrong or account is inactive.If you don't have an account, please sign up using signup link at bottom.")

    return render(request, 'htmlfiles/login.html', {'form': form})


# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


@login_required
def homepage_view(request):  # Accessing username from session
    return render(request, 'htmlfiles/home.html')


@login_required
def aboutpage_view(request):
    about_list=aboutdetails.objects.all()
    first=about_list[0]
    second=about_list[1]
    third=about_list[2]
    fourth=about_list[3]
    return render(request, 'htmlfiles/about.html', {'about_list': about_list, 'first': first, 'second': second, 'third': third, 'fourth': fourth})


@login_required
def aboutdetail_view(request,title):
    about_detail=get_object_or_404(aboutdetails,slug=title) #to get record matched with the slug title
    return render(request, 'htmlfiles/aboutdetail.html', {'about_detail': about_detail})

@login_required
def audiopage_view(request):
    #print(10/0)  # this line is for testing purpose to check if middleware is working for exception handling
    return render(request, 'htmlfiles/audio.html')


@login_required
def gallery_view(request):
    return render(request, 'htmlfiles/gallery.html')


@login_required
def books_view(request):
    return render(request, 'htmlfiles/books.html')

@login_required
def contact_view(request):
    form=contactusForm()
    if request.method == 'POST':
        form=contactusForm(request.POST)
        if form.is_valid():
            cleaned_data=form.cleaned_data
            name = f"{request.user.first_name} {request.user.last_name}".upper()
            email = request.user.email
            subject=form.cleaned_data['subject'].upper()
            message=form.cleaned_data['message']
            contacus.objects.create(name=name, email=email, subject=subject, message=message)
            #sending email using django send_mail function
            full_message=("You have received a query about your website from User-{} about {} \n \n \n {}".format(name,subject,message))
            try:
                send_mail(subject,full_message,email,['test@example.com'],fail_silently=False)
                messages.success(request, "Your request has been noted. We will get back to you soon!")
            except Exception as e:
                print("Error sending email:", e)
                messages.error(request, "There was an error sending your message. Please try again later.")
        return redirect(request.META.get("HTTP_REFERER", "/"))


# """ -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""

#                             THE BELOW ONES ARE FOR MY PRACTICE.[CRUD USING FUNCTION BASED VIEWS] USING FUNCTION BASED VIEWS

def wish_insertview(request):
    form=wishForm()
    if request.method == 'POST':
        form=wishForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/wish/')
    return render(request, 'htmlfiles/wishinsert.html', {'form': form})

def wish_updateview(request,id):
    wish=wishdata.objects.get(id=id) #to get record matched with the id
    form=wishForm(instance=wish)
    if request.method == 'POST':
        form=wishForm(request.POST, instance=wish)
        if form.is_valid():
            form.save()
            return redirect('/wish/')
    return render(request, 'htmlfiles/wishupdate.html', {'form': form})

def wish_deleteview(request,id):
    wish=wishdata.objects.get(id=id) #to get record matched wish data with the id
    wish.delete()
    return redirect('/wish/')

def wish_retrieveview(request):
    #print(request.COOKIES)
    # count = int(request.COOKIES.get('count', 0))
    # count += 1
    #wish_list=wishdata.objects.all() # To get list of all the data in the table
    #wish_list = wishdata.objects.filter(name__startswith='A')  # Django ORM code to fetch all records from wishdata table whose name starts with A
    wish_list=wishdata.objects.all().values_list('name','astrology_message')
    #print(wish_list)
    pagination=Paginator(wish_list,8) #10 records per page #create an object of paginator class
    page_number=request.GET.get('page') #getting the page number from url query parameter
    print(page_number)
    try:
        wish_list=pagination.page(page_number)#getting the records of that particular page number
    except PageNotAnInteger:
        wish_list=pagination.page(1)#getting the first page records if page number is not an integer or if we provide direct url without page number
    except EmptyPage:
        wish_list=pagination.page(pagination.num_pages)#getting the last page records if page number is out of range like if total pages are 10 and we give page number as 100
    response = render(request, 'htmlfiles/wish.html', {'wish_list': wish_list})
    # response.set_cookie('count', count)
    return response


#                             THE BELOW ONES ARE FOR MY PRACTICE.[CRUD USING CLASS BASED VIEWS ]

#THE BELOW ONE IS A NORMAL VIEW CLASS BASED VIEW FOR RETRIEVING WISH DATA
class Wishgetview(View):
    def get(self,request):
        wish_list=wishdata.objects.all()
        return render(request, 'htmlfiles/wish.html', {'wish_list': wish_list})

class Helloworldview(View):
    def get(self,request):
        return HttpResponse("Hello World! This is my first class based view in Django.") #there is no template file associated with this view just returning a simple http response


#THE BELOW ONE IS A TEMPLATE VIEW CLASS BASED VIEW FOR RETRIEVING WISH DATA
class wishgetviewtemplateview(TemplateView):
    template_name = 'htmlfiles/wish.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs) #getting context object from parent class amd it is a dictionary
        context['wish_list'] = wishdata.objects.all() #adding wish_list to context and overriding the get_context_data method with our own data
        return context


            #THE BELOW ONES ARE FOR MODEL RELATED VIEW CLASSES TO PERFORM CRUD OPERATIONS USING CLASS BASED VIEWS: USE IF WE NEED TO PERFORM DB OPERATIONS


class wishcreateview(CreateView):
    model=wishdata
    fields = '__all__'  # to include all fields from the model in the form
     #default template name is 'webapp/wishdata_form.html'
     #create will always call get_absolute_url method of the model to redirect to detail view of the created object

class wishupdateview(UpdateView):
    model=wishdata
    fields = '__all__'  # to include all fields from the model in the form
    #default template name is 'webapp/wishdata_form.html'

class wishdeleteview(DeleteView):
    model=wishdata
    #success_url = '/wishlistcbv2/'  # URL to redirect after successful deletion
    #default template name is 'webapp/wishdata_confirm_delete.html'
    success_url = reverse_lazy('wishlistcbv2')  # using reverse_lazy to avoid circular import issues

class wishlistview(ListView):
    model = wishdata
                                    #the below are optional attributes which are defaulted by django if not provided
    #template_name = 'wishdata_list.html'  # Default is '<app_label>/<model_name>_list.html'
                                    # the below are optional methods which can be overridden to customize the behavior
    #template_name = 'htmlfiles/wish.html'  # this is our custom template name
                                    # the below are optional attributes which are defaulted by django if not provided
    #context_object_name = 'wishdata_list'  # Default is '<model_name>_list'
                                    # the below are optional methods which can be overridden to customize the behavior
    context_object_name = 'wish'
    paginate_by = 10  # Number of items per page

class wishlistview2(ListView):
    model=wishdata
    template_name='webapp/wishlistindex.html'
    context_object_name='wish2'

class wishdetailview(DetailView):
    model=wishdata
    #default template name is 'webapp/wishdata_detail.html'
    #default context object: wishdata(modelclassname) or object






# """def wish_view(request):
#     print(request.COOKIES)
#     count=request.session.get('count', 0) #everything happening at server side using sessions #GETTER
#     count+=1
#     request.session['count'] = count        #SETTER
#     wish_list = wishdata.objects.all()  # To get list of all the data in the table
#     return render(request, 'htmlfiles/wish.html', {'count': count,'wish_list': wish_list})
#
#
#
# def books_view(request):
#     books_list=books.objects.all()   #Django ORM code to fetch all records from books table
#     print(books_list)
#     my_dict={'books_list':books_list}
#     return render(request, 'htmlfiles/books.html', context=my_dict)"""
#
# """def wish_view(request):
#     date=datetime.datetime.now()
#     msg="Hello Friend"
#     hour=int(date.strftime('%H'))
#     if hour<12:
#         msg+=" Good Morning"
#     elif hour<16:
#         msg+=" Good Afternoon"
#     elif hour<20:
#         msg+=" Good Evening"
#     else:
#         msg+=" Good Night"
#     user=['kalyan']
#     names_list=['Ravi','Raju','Sonu','Monu','Sonu','Anu','Manu','Pooja']
#     astrology_list=['You will have a great day!','Success is on the horizon.','Expect the unexpected.','Today is a perfect day to try something new.','Good fortune will come your way.']
#     user=r.choice(user)
#     namechoice=r.choice(names_list)
#     astrology_message=r.choice(astrology_list)
#     my_dict={'date':date,'msg':msg,'names':namechoice,'astrology_message':astrology_message,'user':user}
#     return render(request, 'htmlfiles/wish.html', context=my_dict)"""
