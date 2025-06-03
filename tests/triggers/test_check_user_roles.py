from sqlalchemy.exc import DBAPIError

from models.models import User, UserRole
from models.enums import UserRoleEnum


def test_check_user_roles_raises_error_when_no_roles(db_session):
    employee = User(given_name='employee', family_name='employee', username='employee', password_hash='hash')
    db_session.add(employee)

    user_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(user_role)

    db_session.commit()

    db_session.delete(user_role)

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "User must have at least one role!" in str(e.orig)

def test_check_user_roles_passes_when_user_has_role(db_session):
    employee = User(given_name='employee', family_name='employee', username='employee', password_hash='hash')
    db_session.add(employee)

    user_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(user_role)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False
