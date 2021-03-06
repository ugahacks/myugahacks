from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from django.urls import reverse
from django.utils.safestring import mark_safe
import datetime
from user.models import User


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """
    password = ReadOnlyPasswordHashField(label=("Password"),
                                         help_text=("Passwords are not stored in plaintext, so there is no way to see "
                                                    "this user's password"))

    class Meta:
        model = User
        exclude = []

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=100)
    password = forms.CharField(widget=forms.PasswordInput, label='Password', max_length=100)

    def clean_email(self):
        email = self.cleaned_data.get("email")
        return email.lower()


class RegisterForm(LoginForm):
    password2 = forms.CharField(widget=forms.PasswordInput, label='Repeat password', max_length=100,
                                help_text=' '.join(password_validators_help_texts()))
    name = forms.CharField(label='Full name', max_length=25, help_text='What is your preferred full name?')

    terms_and_conditions = forms.BooleanField(
        label='I\'ve read, understand and accept <a href="https://www.ugahacks.com/privacy" target="_blank">UGAHacks '
              'Privacy Policy</a>.<span style="color: red; font-weight: bold;"> *</span>')

    birthday = forms.DateField(widget=forms.DateInput(format=('%m/%d/%Y'),
            attrs={'class':'form-control', 'type': 'date'}))

    field_order = ['name', 'email', 'password', 'password2', 'birthday', 'terms_and_conditions']

    def clean_password2(self):
        # Check that the two password entries match
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        validate_password(password)
        return password2

    def clean_terms_and_conditions(self):
        cc = self.cleaned_data.get('terms_and_conditions', False)
        # Check that if it's the first submission hackers checks terms and conditions checkbox
        # self.instance.pk is None if there's no Application existing before
        # https://stackoverflow.com/questions/9704067/test-if-django-modelform-has-instance
        if not cc and not self.instance.pk:
            raise forms.ValidationError(
                "In order to apply and attend you have to accept our Terms & Conditions and"
                " our Privacy Policy."
            )
        return cc

    def clean_birthday(self):
        birthday = self.cleaned_data.get('birthday')
        currdate = datetime.datetime.now()
        if datetime.datetime(birthday.year + 18, birthday.month, birthday.day) > currdate:
            raise forms.ValidationError(
                "In order to apply and attend you must be at least 18 years old."
            )
        return birthday

    def clean_email(self):
        email = self.cleaned_data.get("email")
        return email.lower()


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data['email']
        emailcap = self.cleaned_data['email'].capitalize()
        if not User.objects.filter(email=email).exists() and not User.objects.filter(email=emailcap).exists():
            raise forms.ValidationError(
                mark_safe(
                    f"We couldn't find a user with that email address. <a href={reverse('account_signup')} style='color: inherit; text-decoration: underline;'>Why not register an account?</a>")
            )
        elif User.objects.filter(email=email).exists():
            return email
        else:
            return emailcap


class SetPasswordForm(forms.Form):
    """
    A form that lets a user change set their password without entering the old
    password
    """

    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput,
        strip=False,

    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput,
        help_text=' '.join(password_validation.password_validators_help_texts()),
    )

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The passwords do not match.")
        password_validation.validate_password(password2)
        return password2

    def save(self, user):
        password = self.cleaned_data["new_password1"]
        user.set_password(password)
        user.save()
