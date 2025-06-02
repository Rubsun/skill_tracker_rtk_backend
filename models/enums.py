import enum


class UserRoleEnum(enum.Enum):
    """User roles."""
    manager = "manager"
    employee = "employee"


class ContentStatusEnum(enum.Enum):
    """Task statuses."""
    pending = "pending"
    incorrect = "incorrect"
    done = "done"
