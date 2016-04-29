__author__ = 'shamailtayyab'

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
]