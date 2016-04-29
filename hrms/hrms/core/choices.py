__author__ = 'shamailtayyab'
from django.contrib.auth.models import User

class LeaveTypes (object):
    CL = "CasualLeave"
    SL = "SickLeave"
    EL = "EarnedLeave"
    ML = "MaternalLeave"
    ZL = "SpecialLeave"

    @classmethod
    def all (cls):
        return [(cls.CL, "Casual Leave"), (cls.SL, "Sick Leave"), (cls.EL, "Earned Leave"), (cls.ML, "Maternal Leave"), (cls.ZL, "Special Leave")]


departments = [
    ("IT", "Information Technology"),
    ("SALES", "Sales"),
    ("OPERATIONS", "Operations"),
    ("HR", "Human Resource"),
    ("ADMIN", "Administration"),
    ("MARKETING", "Marketing"),
    ("ACCOUNTS", "Accounts"),
]

MANAGERS = {
    "IT": ("atyab", "shamail"),
    "SALES": ("vikrant", "himanshu", "umair"),
    "OPERATIONS": ("himanshu", "umair"),
    "HR": ("himamshu", "umair"),
    "ADMIN": ("atyab", "shamail"),
    "MARKETING": ("vikrant", "himanshu", "umair"),
    "DEVOPS": ("himanshu", "gaurav"),
    "ACCOUNTS": ("himanshu", "umair"),
}

def get_managers (foruser):
    managers = MANAGERS[foruser.userprofile.department]
    emails = []
    for m in managers:
        try:
            user = User.objects.get (username = m)
        except User.DoesNotExist:
            print "Couldn't select", m
            continue
        emails.append (user.email)
    print "Seleting managers", emails
    return emails

def get_departments (foradmin):
    mydepts = set()
    for dept, admins in MANAGERS.items():
        for a in admins:
            if foradmin.username == a:
                mydepts.add (dept)

    return list (mydepts)

