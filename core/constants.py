DAYS_OF_WEEK = (
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
)


AVAILABLE_TIMES = (
    ('0', '9:00 - 11:00'),
    ('1', '12:00 - 14:00'),
    ('2', '14:00 - 16:00'),
)

SATISFACTION_LEVELS = (
    ('0', 'Very satisfied'),
    ('1', 'Satisfied'),
    ('2', 'OK'),
    ('3', 'Dissatisfied'),
    ('4', 'Very dissatisfied'),
)

# https://stackoverflow.com/questions/16699007/regular-expression-to-match-standard-10-digit-phone-number
PHONE_REGEX = r'^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$'

# TODO update.
STUDENT_ID_REGEX = r'^[A-Za-z]{5}\d{3}$'
