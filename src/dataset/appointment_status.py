from enum import Enum


class AppointmentStatus(Enum):
    APPROVED = 'approved'
    STARTED = 'started'
    COMPLETED = 'completed'
    NO_SHOW = 'no_show'
    CANCELLED = 'cancelled'
    VALID_SCHEDULED = [APPROVED, STARTED, COMPLETED]
    VALID_COMPLETED = [STARTED, COMPLETED]
    VALID_CANCELLED = [CANCELLED, NO_SHOW]
