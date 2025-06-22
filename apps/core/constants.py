from uuid import uuid4
USER_ROLES = (
    ("Admin", "Admin"),
    ("Staff", "Staff"),
    ("Student", "Student"),
)


GENDER_CHOICES = ["Male", "Female"]
SOURCES = [
    "Email",
    "Social Media",
    "Phone",
    "Website",
    "Webinar",
    "Event",
    "Campaign",
    "Referral",
    "Other",
]

INTERACTION_TYPES = ["Email", "Phone", "SMS", " Meeting", "Event"]

LEAD_STAGES = [
    "New",
    "Contacted",
    "Interested",
    "Application in Progress",
    "Converted",
    "Lost",
]

SEMESTER_TYPES = ["Semester One", "Semester Two", "Semester Three"]
ACADEMIC_YEARS = [
    "First Year",
    "Second Year",
    "Third Year",
    "Fourth Year",
    "Fifth Year",
    "Sixth Year",
    "Seventh Year",
]
SESSION_STATUSES = ["Future", "Active", "Cancelled", "Completed", "Rescheduled"]

MONTHS_LIST = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


LEAVE_TYPES = [
    "Sick Leave",
    "Vacation Leave",
    "Annual Leave",
    "Maternity Leave",
    "Paternity Leave",
    "Unpaid Leave",
    "Casual Leave",
    "Privilege Leave",
    "Study Leave",
    "Emergency Leave",
    "Other",
]


def payment_ref_generator():
    return uuid4().hex