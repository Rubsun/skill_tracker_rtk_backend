from sqlalchemy.exc import DBAPIError
from models.models import User, UserRole, Course, Content, Task
from models.enums import UserRoleEnum


def test_protect_task_update_after_course_produced(db_session):
    manager = User(given_name='manager', family_name='manager', username='manager', password_hash='hash')
    db_session.add(manager)

    db_session.add(UserRole(user=manager, role=UserRoleEnum.manager))
    db_session.flush()

    course = Course(title='title', manager_id=manager.id, is_produced=True)
    db_session.add(course)
    db_session.flush()

    task = Task(question='question', answer='answer')
    db_session.add(task)
    db_session.flush()

    content = Content(title='title', course_id=course.id, task_id=task.id)
    db_session.add(content)

    db_session.commit()

    task.question = 'new question'

    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert 'Cannot update task after course is produced!' in str(e.orig)
