__author__ = 'shamailtayyab'

from django import forms
from django.contrib.auth import authenticate
from django.forms import ModelForm

from hrms.core.choices import LeaveTypes
from hrms.core.models import UserProfile, Holiday
from django.contrib.auth.models import User
import datetime

class LoginForm (forms.Form):
    employeeid = forms.CharField (label='EmployeeID', max_length=100)
    password = forms.CharField (label='Password', max_length=100, widget=forms.PasswordInput())

    def clean (self):
        cleaned_data = super(LoginForm, self).clean()
        emp_id = cleaned_data.get ("employeeid")
        password = cleaned_data.get ("password")

        self.user = authenticate (username=emp_id, password=password)

        if self.user is not None:
            # the password verified for the user
            if self.user.is_active:
                return
            else:
                raise forms.ValidationError ("This user is inactive, contact Wigzo System Administrator to activate.")
        else:
            raise forms.ValidationError ("Please check the username or password.")


def year_choice_generator ():
    today = datetime.datetime.today()
    year_choices = (today.year, today.year+1)
    return year_choices

class LeaveForm (forms.Form):
    leave_type = forms.ChoiceField (choices = LeaveTypes.all())
    from_ = forms.DateField (widget=forms.SelectDateWidget(years=year_choice_generator()))
    to = forms.DateField (widget=forms.SelectDateWidget(years=year_choice_generator()))

    partial = forms.ChoiceField (choices = [("full", "Full Day"), ("half", "Half Day")])
    reason = forms.CharField (max_length = 256, widget=forms.Textarea())

    def clean (self):
        cleaned_data = super(LeaveForm, self).clean()
        if cleaned_data.get ("from_") > cleaned_data.get ("to"):
            raise forms.ValidationError ("Start date is greater than end date")
        delta = cleaned_data.get ("to") - cleaned_data.get ("from_")
        if delta.days > 10:
            raise forms.ValidationError ("Woah! Cannot apply that many leaves. Why not talk with your manager first?")

class UserEditForm (ModelForm):
    class Meta:
        model = UserProfile
        fields = ['gender', 'address', 'pan', 'primary_phone', 'emergency_contact', 'actualdob', 'documenteddob', 'department']
        widgets = {
            'gender': forms.Select (choices = [("male","Male"), ("female", "Female")]),
            'actualdob': forms.SelectDateWidget(years=range(1950, 2000)),
            'documenteddob': forms.SelectDateWidget(years=range(1950, 2000)),
            "department": forms.Select (choices = [("IT", "Information Technology")])
        }

class UserForm (ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name', 'email']

class HolidayForm (ModelForm):
    class Meta:
        model = Holiday
        fields = ['name', 'falling_on']
        widgets = {
            'falling_on': forms.SelectDateWidget(years=range(datetime.datetime.today().year, datetime.datetime.today().year)),
        }

class PasswordForm (forms.Form):
    user = forms.CharField (max_length=100, widget=forms.HiddenInput())
    oldpassword = forms.CharField (label='Old Password', max_length=100, widget=forms.PasswordInput())
    newpassword= forms.CharField (label='Set new Password', max_length=100, widget=forms.PasswordInput())
    retypepassword = forms.CharField (label='Retype new Password', max_length=100, widget=forms.PasswordInput())

    def clean (self):
        cleaned_data = super(PasswordForm, self).clean()
        user = cleaned_data.get ("user")
        oldpassword = cleaned_data.get ("oldpassword")
        newpassword = cleaned_data.get ("newpassword")
        retypepassword = cleaned_data.get ("retypepassword")

        self.user = authenticate (username=user, password=oldpassword)
        if self.user is None:
            raise forms.ValidationError ("Old password is not correct!")

        if newpassword != retypepassword:
            raise forms.ValidationError ("Both the input passwords should match!")


