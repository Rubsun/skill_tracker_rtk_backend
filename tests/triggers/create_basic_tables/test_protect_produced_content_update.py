from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course, Content, Task
from models.enums import UserRoleEnum


def test_protect_produced_content_update(db_session):
    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    db_session.add(manager)

    db_session.add(UserRole(user=manager, role=UserRoleEnum.manager))
    db_session.flush()

    course = Course(title='course', manager_id=manager.id, is_produced=True)
    db_session.add(course)
    db_session.flush()

    task = Task(question='question', answer='answer')
    db_session.add(task)
    db_session.flush()

    content = Content(title='title', course_id=course.id, task_id=task.id)
    db_session.add(content)

    db_session.commit()

    content.title = 'new title'

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert 'Only deadline can be updated after course is produced!' in str(e.orig)
