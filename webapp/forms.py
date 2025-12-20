from django import forms
import re
from webapp.models import *
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.core import validators
"""------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
"""class Form:
    def __init__(self):
        self.cleaned_data = {'loginemail': 'ckalyan.2020@gmail.com', 'loginpassword': ''}"""

"""------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
class signupForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['username','first_name','last_name','email','password']

    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm mb-4',
            'placeholder': 'Enter your Username'
        })
    )
    first_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm mb-4',
            'placeholder': 'Enter your First name'
        })
    )
    last_name = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-sm mb-4',
            'placeholder': 'Enter your Last name'

        })
    )
    email = forms.CharField(
        label='',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-sm mb-4',
            'placeholder': 'Email Address'
        })
    )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-sm mb-4',
            'placeholder': 'Set your Password'
        })
    )
    bothandler = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean(self):
        total_cleaned_data = super().clean()
        username = total_cleaned_data['username']
        email = total_cleaned_data.get('email')
        if email:
            email=email.lower()
            total_cleaned_data['email']=email
        if not email:
            raise forms.ValidationError("Please enter a valid email address")
        if not (email.endswith('.com')) or ('@' not in email):
            raise forms.ValidationError("Invalid email address please enter valid email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.If you forgot your password please go to forgot password page to reset your password")
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'
        password = total_cleaned_data['password']
        if not re.search(pattern, password):
            raise forms.ValidationError("Password must contain at least 8 characters and should contain at least one uppercase letter, one lowercase letter, one digit, and one special character:@$!%*?&#")
        bothandler = total_cleaned_data['bothandler']
        if len(bothandler) > 0:
            raise forms.ValidationError("Dont play with my website")

"""--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""

class resetpasswordForm(forms.Form):
    email = forms.EmailField(
        label="",
        widget=forms.EmailInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Email Address'
        })
    )
    newpassword  = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Password'
        })
    )
    confirmpassword  = forms.CharField(
        label="",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Confirm new password'
        })
    )
    bothandler = forms.CharField(required=False, widget=forms.HiddenInput())

    def clean(self):
        total_cleaned_data = super().clean()
        print("Validating password and confirm password together in a single clean method")
        email=total_cleaned_data['email']
        if email and not User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is not registered. Please enter a valid registered email or signup one if you don't have an account.")
        newpassword = total_cleaned_data['newpassword']
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'
        if not re.search(pattern, newpassword):
            raise forms.ValidationError("Password must contain at least 8 characters and should contain at least one uppercase letter, one lowercase letter, one digit, and one special character:@$!%*?&#")
        confirmpassword = total_cleaned_data['confirmpassword']
        if newpassword != confirmpassword:
            raise forms.ValidationError("Password and Confirm Password do not match please enter same password in both fields")
        bothandler = total_cleaned_data['bothandler']
        if len(bothandler) > 0:
            raise forms.ValidationError("Dont play with my website")


"""---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------"""
"""def validate_email_domain(value):
    if '@gmail.com' not in value:
        raise forms.ValidationError("Email must be a gmail address.")
   so in below form for the in the place of inbuilt core validators we can use  our own custom validator function like this validators=[validate_email_domain]
    OR IF U WANT TO USE INBUILT VALIDATORS=[VALIDATORS.MAXLENGHT(),VALIDATORS.MINLENGHT(10)] INSDIE THAT PARTICULAR FORM FIELD EXCLUSVELY------------ PAGE 60 IN DJANGO BOOK"""


class loginForm(forms.ModelForm):
    class Meta:
        model = loginFormdata
        fields = '__all__'

    loginemail = forms.CharField(
        label="",
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-sm mb-3', 'placeholder': 'Enter your email'})
    )
    loginpassword = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={'class': 'form-control form-control-sm mb-3', 'placeholder': 'Enter your password'})
    )
    bothandler = forms.CharField(required=False,widget=forms.HiddenInput())

    """ THE BELOW ONE IS A FORM LEVEL SINGLE CLEAN METHOD USED FOR VALIDATING MULTIPLE FIELDS TOGETHER"""

    def clean(self):
        total_cleaned_data = super().clean()
        print("Validating email and password together in clean method")
        loginemail = total_cleaned_data['loginemail']
        if not loginemail:
            raise forms.ValidationError("Email field cannot be empty")
        if not loginemail.endswith('.com') or ('@' not in loginemail):
            raise forms.ValidationError("Invalid email address please enter valid email")
        pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'
        loginpassword = total_cleaned_data['loginpassword']
        if not re.search(pattern, loginpassword):
            raise forms.ValidationError(
                "Password must contain at least 8 characters and should contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character:@$!%*?&#")
        bothandler=total_cleaned_data['bothandler']
        if len(bothandler)>0:
            raise forms.ValidationError("Dont play with my website")
        return total_cleaned_data


    #----------------------------THE BELOW ONES ARE FIELD LEVEL CLEAN METHODS USED FOR VALIDATING INDIVIDUAL FIELDS--------------------------------------------------------------------
    #
    #                                                             Here’s what each part means:
    # ^ means the start of the password.
    # (?=.*[a-z]) means the password must contain at least one lowercase letter (a to z).
    # (?=.*[A-Z]) means it must contain at least one uppercase letter (A to Z).
    # (?=.*\d) means it must contain at least one number (0 to 9).
    # (?=.*[@$!%*?&#]) means it must contain at least one special character from the list: @ $ ! % * ? & #
    # [A-Za-z\d@$!%*?&#]{8,} means the password can only contain uppercase letters, lowercase letters, numbers, and those special symbols — and it must be at least 8 characters long.
    # $ means the end of the password.
    # So when all combined, this pattern says:The entire password must be at least 8 characters long and must include at least one lowercase letter, one uppercase letter, one digit, and one special character."""
    #
    # """def clean_loginemail(self):
    #     email = self.cleaned_data['loginemail']
    #     if not email.endswith('.com') or ('@' not in email):
    #         raise forms.ValidationError("Invalid email address please enter valid email")
    #     return email
    #
    # def clean_loginpassword(self):
    #     password = self.cleaned_data['loginpassword']
    #     pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$'
    #     if not re.search(pattern, password):
    #         raise forms.ValidationError(
    #             "Password must contain at least 8 characters and should contain at least one uppercase letter, "
    #             "one lowercase letter, one digit, and one special character:@$!%*?&#")
    #     return password

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class contactusForm(forms.ModelForm):

    class Meta:
        model=contacus
        fields=['subject','message']

    subject=forms.ChoiceField(
        choices=CATEGORY_CHOICES,
        label="",
        widget=forms.Select(attrs={
            'class': 'form-control form-control-sm mb-4',
        })
    )
    message = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'class': 'form-control form-control-sm mb-4',
            'placeholder': 'Enter your message here',
            'rows': 4,
        })
    )




#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#THE BELOW MODEL IS A TEMPORARY FORM TO STORE THE WISH DATA FOR MY PRACTICE
class wishForm(forms.ModelForm):
    class Meta:
        model=wishdata
        fields='__all__'

    def clean(self):
        total_cleaned_data = super().clean()
        mobilenumber = total_cleaned_data['mobilenumber']
        if mobilenumber <= 0:
            raise forms.ValidationError("Mobile number should be a positive number")
        if len(str(mobilenumber)) != 10:
            raise forms.ValidationError("Mobile number should be exactly 10 digits long")
        name=total_cleaned_data['name']
        if not all(x.isalpha() or x.isspace() for x in name):
            raise forms.ValidationError("Name should contain only alphabetic characters and spaces")
        username=total_cleaned_data['username']
        has_alpha=any(x.isalpha() for x in username)
        has_digit=any(x.isdigit() for x in username)
        if not (has_alpha and has_digit):
            raise forms.ValidationError("Username should contain both alphabetic characters and numbers,(no special characters).")
        return total_cleaned_data


