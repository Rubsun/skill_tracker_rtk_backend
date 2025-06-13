from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course, Content, Task
from models.enums import UserRoleEnum


def test_validate_course_deadline_not_before_content(db_session):
    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    db_session.add(manager)

    db_session.add(UserRole(user=manager, role=UserRoleEnum.manager))
    db_session.flush()

    course = Course(title='Deadline Test', manager_id=manager.id)
    db_session.add(course)
    db_session.flush()

    task = Task(question='question', answer='answer')
    db_session.add(task)
    db_session.flush()

    content = Content(title='Content D', course_id=course.id, task_id=task.id, deadline='2025-12-31T00:00:00+00:00')
    db_session.add(content)

    db_session.commit()

    course.deadline = '2025-12-01T00:00:00+00:00'

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert 'Course deadline (2025-12-01 00:00:00+00s) cannot be earlier than latest content deadline (2025-12-31 00:00:00+00s)!' in str(e.orig)
