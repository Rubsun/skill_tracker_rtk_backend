from sqlalchemy.exc import DBAPIError

from models.models import User, UserRole, Course, Task, Theory, Content
from models.enums import UserRoleEnum


def test_check_content_type_task_theory_raises_error_two_fields_filled_in(db_session):
    """
    Test that creating Content with both task_id and theory_id set raises a DBAPIError.
    This enforces the rule that only one of these fields can be filled at the same time.
    """
    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    db_session.add(manager)

    user_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title='title', manager_id=manager.id)
    task = Task(question='question', answer='answer')
    theory = Theory(text='text')
    db_session.add_all([course, task, theory])

    db_session.flush()

    content = Content(title='title', course_id=course.id, task_id=task.id, theory_id=theory.id)
    db_session.add(content)
    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "The task_id and theory_id fields cannot be filled in at the same time!" in str(e.orig)


def test_check_content_type_task_theory_raises_error_two_fields_empty(db_session):
    """
    Test that creating Content with neither task_id nor theory_id set raises a DBAPIError.
    This enforces the rule that one of these fields must be filled.
    """
    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    db_session.add(manager)

    user_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title='title', manager_id=manager.id)
    db_session.add(course)

    db_session.flush()

    content = Content(title='title', course_id=course.id, task_id=None, theory_id=None)
    db_session.add(content)
    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "One of the task_id or theory_id fields must be filled in!" in str(e.orig)


def test_check_content_type_task_theory_passes(db_session):
    """
    Test that creating Content with exactly one of task_id or theory_id set commits successfully.
    Validates that the constraint on content type is enforced correctly.
    """
    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    db_session.add(manager)

    user_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title='title', manager_id=manager.id)
    task = Task(question='question', answer='answer')
    theory = Theory(text='text')
    db_session.add_all([course, task, theory])

    db_session.flush()

    content = Content(title='title', course_id=course.id, deadline=None, task_id=task.id, theory_id=None)
    db_session.add(content)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False

    content2 = Content(title='title', course_id=course.id, deadline=None, task_id=None, theory_id=theory.id)
    db_session.add(content2)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False
