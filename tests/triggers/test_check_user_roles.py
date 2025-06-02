from sqlalchemy.exc import DBAPIError

from models.models import User, UserRole
from models.enums import UserRoleEnum


def test_check_user_roles_raises_error_when_no_roles(db_session):
    user = User(given_name='Иван', family_name='Иванов', username='ivan', password_hash='hash')
    db_session.add(user)

    user_role = UserRole(user=user, role=UserRoleEnum.employee)
    db_session.add(user_role)

    db_session.commit()

    try:
        db_session.delete(user_role)
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "User must have at least one role!" in str(e.orig)

def test_check_user_roles_passes_when_user_has_role(db_session):
    user = User(given_name='Иван', family_name='Иванов', username='ivan', password_hash='hash')
    db_session.add(user)

    user_role = UserRole(user=user, role=UserRoleEnum.employee)
    db_session.add(user_role)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False
