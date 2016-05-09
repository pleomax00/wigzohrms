from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models import Q
from django.conf import settings
from hrms.core.choices import LeaveTypes, get_managers
from hrms.core.lib import wigzomail
from decimal import Decimal
import datetime
import math

class UserProfile (models.Model):
    user = models.OneToOneField (User)
    gender = models.CharField (max_length=140)
    address = models.CharField (max_length=140)
    pan = models.CharField (max_length=10, default = "")
    primary_phone = models.CharField (max_length=12, default = "")
    emergency_contact = models.CharField (max_length=12, default = "")
    actualdob = models.DateField (default = datetime.date (2015, 1, 1))
    documenteddob = models.DateField (default = datetime.date (2015, 1, 1))
    joiningdate = models.DateField (default = datetime.date (2015, 1, 1))
    department = models.CharField (max_length=140, default = "IT")

    def __unicode__(self):
        return u'Profile of user: %s' % self.user.username

    @classmethod
    def upcoming_birthdays (cls):
        today = datetime.date.today()
        looktill = today + datetime.timedelta (days = 60)

        upcominghld = []
        for profile in cls.objects.all ():
            if profile.actualdob is None:
                continue
            lookfor = datetime.date (today.year, profile.actualdob.month, profile.actualdob.day)

            if lookfor < looktill and lookfor > today:
                upcominghld.append ((profile.user, looktill))

        upcominghld = sorted(upcominghld, key = lambda x: x[1], reverse=True)
        upcominghld = map (lambda x: x[0], upcominghld)
        return upcominghld


def create_user_profile (sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Leave (models.Model):
    user = models.ForeignKey (User)
    leave_type = models.CharField (max_length = 32)
    leave_part = models.DecimalField (max_digits = 4, decimal_places = 1, default = Decimal('1.0'))
    date = models.DateField ()

    approval_status = models.CharField (default = "pending", max_length = 32)
    approved_statuschange_on = models.DateField (default = datetime.datetime.today)
    approved_statuschange_by = models.ForeignKey (User, related_name = "statuschangeby")

    reason = models.CharField (max_length = 256, default = "")

    @classmethod
    def byId (cls, leave_id):
        try:
            return cls.objects.get (id = leave_id)
        except cls.DoesNotExist:
            return None

    @classmethod
    def was_on_leave (cls, user, on_date):
        try:
            leave = cls.objects.get (user = user, date = on_date)
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def apply (cls, user, leave_type, leave_part, from_, to, reason):
        day = datetime.timedelta(days=1)
        applied = 0
        body = "Hi\n\nPlease visit http://intranet.wigzo.com to approve or reject.\nReason stated: %s\n\nThanks\nWigzo Intranet." % (reason)
        while from_ <= to:
            application_date = from_
            from_ = from_ + day
            burn = Decimal('0.5') if leave_part == "half" else Decimal ('1.0')
            if cls.was_on_leave (user, application_date):
                continue
            if Holiday.is_holiday_on (application_date):
                continue
            if Holiday.is_weekend_on (application_date):
                continue
            leave = cls (user = user, leave_type = leave_type, leave_part = burn, date = application_date, reason = reason)
            leave.approved_statuschange_by = user
            leave.approved_statuschange_on = datetime.datetime.today()
            leave.save ()
            applied += 1

        if applied > 0:
            wigzomail (get_managers (user), "%s has applied for %d %s(s)." %(user.get_full_name(), applied, leave_type), body)


    @classmethod
    def of_user (cls, user, ltype, year):
        if year is None:
            year = datetime.datetime.today().year
        if year == -1:
            leaves = cls.objects.filter (Q(approval_status="accepted") | Q(approval_status="pending"), Q(user = user), Q(leave_type = ltype)).order_by ("-date")
        else:
            leaves = cls.objects.filter (Q(approval_status="accepted") | Q(approval_status="pending"), Q(user = user), Q(leave_type = ltype), Q(date__year = year)).order_by ("-date")
        return leaves

    @classmethod
    def counts_of_user (cls, user, year = None):
        cl = sum (x.leave_part for x in cls.of_user(user, LeaveTypes.CL, year))
        sl = sum (x.leave_part for x in cls.of_user(user, LeaveTypes.SL, year))
        ml = sum (x.leave_part for x in cls.of_user(user, LeaveTypes.ML, year))
        zl = sum (x.leave_part for x in cls.of_user(user, LeaveTypes.ZL, year))
        el = sum (x.leave_part for x in cls.of_user(user, LeaveTypes.EL, -1))

        joined = user.userprofile.joiningdate
        today = datetime.datetime.today()
        current_year = today.year

        total_cl = 6
        total_sl = 6

        if joined.year == current_year:
            days = joined.timetuple().tm_yday
            pro_rata = 1 - (days*1.0)/365
            total_cl = math.ceil (pro_rata * total_cl)
            total_sl = math.ceil (pro_rata * total_sl)

        el_policy_date = datetime.date (2016, 03, 01)

        count_from = joined if joined > el_policy_date else el_policy_date
        months_worked = (today.year - count_from.year)*12 + today.month - count_from.month
        total_el = math.floor (months_worked) * 1.25

        return (cl, total_cl, sl, total_sl, el, total_el, ml, zl)

    @classmethod
    def track_record_of_user (cls, user, year = None):
        if year is None:
            year = datetime.datetime.today().year
        leaves = cls.objects.filter (user = user, date__year = year).order_by ("-date")
        return leaves

    @classmethod
    def get_pending (cls):
        return cls.objects.filter (approval_status = "pending")

    def approve (self, byuser, accept):
        new_status = "accepted" if accept == "accept" else "rejected"
        self.approval_status = new_status
        self.approved_statuschange_by = byuser
        self.approved_statuschange_on = datetime.datetime.today()
        self.save ()

    def print_balance (self):
        cl, total_cl, sl, total_sl, el, total_el, ml, zl = Leave.counts_of_user (self.user)
        if self.leave_type == "CasualLeave":
            return "%1.1f / %1.1f" % (cl, total_cl)
        if self.leave_type == "SickLeave":
            return "%1.1f / %1.1f" % (sl, total_sl)
        if self.leave_type == "EarnedLeave":
            return "%1.1f / %1.1f" % (el, total_el)
        if self.leave_type == "MaternalLeave":
            return "%1.1f / inf" % (ml)
        if self.leave_type == "SpecialLeave":
            return "%1.1f / inf" % (zl)

class Holiday (models.Model):
    name = models.CharField (max_length = 32)
    falling_on = models.DateField (default = datetime.datetime.today)

    @classmethod
    def for_year (cls, year):
        return cls.objects.filter (falling_on__year = year)


    @classmethod
    def byId (cls, iid):
        try:
            return cls.objects.get (id = iid)
        except cls.DoesNotExist:
            return None

    @classmethod
    def upcoming (cls):
        today = datetime.date.today()
        #looktill = today + datetime.timedelta (days = 60)

        return cls.objects.filter (falling_on__gt = today).order_by ('falling_on')[:4]

    @classmethod
    def is_holiday_on (cls, idate):
        try:
            cls.objects.get (falling_on = idate)
            return True
        except cls.DoesNotExist:
            return False

    @classmethod
    def is_weekend_on (cls, idate):
        weekday = idate.weekday()
        if weekday == 5 or weekday == 6:
            return True
        return False
