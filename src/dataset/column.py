from enum import Enum


class Column(Enum):
    ID = 'id'
    DATE = 'date'
    STAFF_EMAIL = 'staff_email'
    APPOINTMENT_TYPE = 'type'
    STUDENT_EMAIL = 'stu_email'
    STUDENT_COLLEGE = 'college'
    STUDENT_MAJOR = 'major'
    STUDENT_CLASS = 'class'
    STUDENT_CARD_ID = 'card_id'
    STUDENT_FIRST_NAME = 'fname'
    STUDENT_PREFERRED_NAME = 'pref_name'
    STUDENT_LAST_NAME = 'lname'
    STATUS = 'status'
    DATE_SCHEDULED = 'date_scheduled'
    UNIQUE_REFERRAL = 'unique_referral'
