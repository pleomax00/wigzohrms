from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from hrms.core.choices import get_departments

from hrms.core.models import Leave, Holiday
from hrms.core.forms import UserEditForm, UserForm, LeaveForm, HolidayForm
from django.contrib.auth.models import User

import datetime

@staff_member_required
def superuser (request):
    all_requests = Leave.get_pending ()
    mydepts = get_departments (request.user)

    pending_requests = []
    for r in all_requests:
        if r.user.userprofile.department in mydepts or request.user.is_superuser:
            pending_requests.append (r)

    return render (request, "superuser.html", locals())

@staff_member_required
def removeleave (request, leaveid):
    #print userid, action
    print request.META
    leave = Leave.byId (leaveid)
    if leave is None:
        return HttpResponseRedirect ("/su/?action=nosuchleave")
    leave.delete ()
    return HttpResponseRedirect (request.GET.get ("next", "/"))

@staff_member_required
def leaveaction (request, leaveid, action):
    #print userid, action
    leave = Leave.byId (leaveid)
    if leave is None:
        return HttpResponseRedirect ("/su/?action=nosuchleave")
    leave.approve (request.user, action)
    return HttpResponseRedirect ("/su/?action=done")

@staff_member_required
def users (request):

    users = User.objects.all ()
    return render (request, "suusers.html", locals())

@staff_member_required
def edituser (request, uid):
    user = User.objects.get (id = uid)

    if request.method == "POST":
        userform = UserEditForm (request.POST, instance = user.userprofile)
        if userform.is_valid ():
            userform.save ()
    else:
        userform = UserEditForm (instance = user.userprofile)
    return render (request, "edituser.html", locals())

@staff_member_required
def createuser (request):
    if request.method == "POST":
        userform = UserForm (request.POST)
        if userform.is_valid ():
            u = userform.save ()
            u.set_password (userform.cleaned_data["password"])
            u.save ()
            return HttpResponseRedirect ("/su/users/?created=true")
    else:
        userform = UserForm ()
    return render (request, "createuser.html", locals())

@staff_member_required
def filealeave (request):
    employees = User.objects.all ()
    if request.method == "POST":
        leaveform = LeaveForm (request.POST)
        u = User.objects.get (id = request.POST.get ("employee"))
        if leaveform.is_valid ():
            from_ = leaveform.cleaned_data["from_"]
            to = leaveform.cleaned_data["to"]
            Leave.apply (u, leaveform.cleaned_data["leave_type"], leaveform.cleaned_data["partial"], from_, to, leaveform.cleaned_data["reason"])

            return HttpResponseRedirect ("/su/?created=true")
    else:
        leaveform = LeaveForm ()
    return render (request, "filealeave.html", locals())


@staff_member_required
def calendar (request, year = None):
    if year is None:
        return HttpResponseRedirect ("/su/calendar/%d" % (datetime.date.today().year))

    if request.method == "POST":
        holidayform = HolidayForm (request.POST)
        if holidayform.is_valid ():
            holidayform.save ()
            return HttpResponseRedirect ("/su/calendar/%s?saved=true" % (str (year)))
    else:
        holidayform = HolidayForm ()

    holidays = Holiday.for_year (year)
    return render (request, "calendar.html", locals())

@staff_member_required
def rmcalendar (request, cid):
    holiday = Holiday.byId (cid)
    holiday.delete ()
    next = request.GET.get ("next", datetime.datetime.today().year)
    return HttpResponseRedirect ("/su/calendar/%s?action=deleted" % (str (next)))
