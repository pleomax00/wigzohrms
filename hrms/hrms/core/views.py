from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.conf import settings

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout

from hrms.core.forms import LoginForm, LeaveForm, PasswordForm
from hrms.core.models import Leave, UserProfile, Holiday
from django.contrib.auth.models import User

import datetime
import markdown, os

@login_required
def indexpage (request):
    #profile = request.
    this_year = datetime.datetime.today().year
    cl, total_cl, sl, total_sl, el, total_el, ml, zl = Leave.counts_of_user (request.user, this_year)

    upcomingbday = UserProfile.upcoming_birthdays()
    upcomingholidays = Holiday.upcoming ()
    reporting_managers = request.user.userprofile.get_all_managers

    return render (request, "index.html", locals())

@login_required
def leavespage (request):
    user = request.user
    if request.GET.has_key ("viewfor") and request.user.is_staff:
        user = User.objects.get (id = request.GET.get ("viewfor"))
    this_year = datetime.datetime.today().year
    cl, total_cl, sl, total_sl, el, total_el, ml, zl = Leave.counts_of_user (user, this_year)
    trackrecord = Leave.track_record_of_user (user, this_year)
    allusers = User.objects.all ()

    return render (request, "leaves.html", locals())

@login_required
def calendarpage (request, year = None):
    if year is None:
        return HttpResponseRedirect ("/calendar/%d/" % (datetime.date.today().year))

    holidays = Holiday.for_year(year)

    return render (request, "viewcalendar.html", locals())

@login_required
def account (request):
    if request.method == "POST":
        passwordform = PasswordForm (request.POST)
        if passwordform.is_valid ():
            request.user.set_password (passwordform.cleaned_data["newpassword"])
            request.user.save()
            return HttpResponseRedirect ("/account/?changepassword=true")
    else:
        passwordform = PasswordForm (initial = {"user": request.user.username})

    return render (request, "account.html", locals())

@login_required
def policies (request, pagename):
    index_path = os.path.join (settings.MARKDOWN_PATH, "toc.md")
    content_path = os.path.join (settings.MARKDOWN_PATH, pagename+".md")

    index = markdown.markdown(file (index_path).read(), extensions = ['markdown.extensions.tables'])
    content = markdown.markdown(file (content_path).read(), extensions = ['markdown.extensions.tables'])

    return render (request, "markdown.html", locals())

@login_required
def timesheet (request):
    return render (request, "timesheet.html", locals())

@login_required
def applyleave (request):
    if request.method == "POST":
        leaveform = LeaveForm (request.POST)
        if leaveform.is_valid ():
            from_ = leaveform.cleaned_data["from_"]
            to = leaveform.cleaned_data["to"]
            Leave.apply (request.user, leaveform.cleaned_data["leave_type"], leaveform.cleaned_data["partial"], from_, to, leaveform.cleaned_data["reason"])
            return HttpResponseRedirect ("/leaves/?applied=true")
    else:
        leaveform = LeaveForm ()
    return render (request, "apply.html", locals())

def loginpage (request):
    if request.method == "POST":
        loginform = LoginForm(request.POST)
        if loginform.is_valid ():
            login (request, loginform.user)
            return HttpResponseRedirect (request.GET.get ("next", "/"))
    else:
        loginform = LoginForm ()

    return render (request, "login.html", locals())

def logoutpage (request):
    logout (request)
    return HttpResponseRedirect ("/")
