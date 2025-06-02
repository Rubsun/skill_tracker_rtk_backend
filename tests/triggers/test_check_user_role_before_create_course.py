from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course
from models.enums import UserRoleEnum


def test_check_course_manager_role_raises_error(db_session):
    user = User(given_name='Иван', family_name='Иванов', username='no_manager', password_hash='hash')
    db_session.add(user)
    db_session.flush()

    course = Course(title="Test Course", manager_id=user.id)
    db_session.add(course)

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "Курс может быть создан только пользователем с ролью manager!" in str(e.orig)


def test_check_course_manager_role_passes(db_session):
    user = User(given_name='Иван', family_name='Иванов', username='yes_manager', password_hash='hash')
    db_session.add(user)

    user_role = UserRole(user=user, role=UserRoleEnum.manager)
    db_session.add(user_role)
    db_session.flush()

    course = Course(title="Valid Course", manager_id=user.id)
    db_session.add(course)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False
