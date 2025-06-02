from sqlalchemy.exc import DBAPIError

from models.models import User, UserRole, Course, Task, Theory, Content
from models.enums import UserRoleEnum


def test_check_content_type_task_theory_raises_error(db_session):
    user = User(given_name='Иван', family_name='Иванов', username='ivan', password_hash='hash')
    db_session.add(user)

    user_role = UserRole(user=user, role=UserRoleEnum.manager)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title='title', manager_id=user.id)
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
        assert "Поля task_id и theory_id не могут быть заполнены одновременно!" in str(e.orig)

    db_session.rollback()

    content = Content(title='title', course_id=course.id, task_id=None, theory_id=None)
    db_session.add(content)
    try:
        db_session.commit()
        assert False
    except DBAPIError as e:
        assert "Одно из полей task_id или theory_id должно быть заполнено!" in str(e.orig)

def test_check_content_type_task_theory_passes(db_session):
    user = User(given_name='Иван', family_name='Иванов', username='ivan', password_hash='hash')
    db_session.add(user)

    user_role = UserRole(user=user, role=UserRoleEnum.manager)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title='title', manager_id=user.id)
    task = Task(question='question', answer='answer')
    theory = Theory(text='text')
    db_session.add_all([course, task, theory])

    db_session.flush()

    content = Content(title='content', course_id=course.id, deadline=None, task_id=task.id, theory_id=None)
    db_session.add(content)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False

    content2 = Content(title='content2', course_id=course.id, deadline=None, task_id=None, theory_id=theory.id)
    db_session.add(content2)

    try:
        db_session.commit()
        assert True
    except Exception:
        assert False
