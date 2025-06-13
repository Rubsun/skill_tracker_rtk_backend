from models.models import User, UserRole, Course, Content, CourseEmployee, CourseEmployeeContent, Task, Theory
from models.enums import UserRoleEnum, ContentStatusEnum


def test_create_course_employee_contents(db_session):
    """
    Test that when a user with employee role is registered to a course,
    CourseEmployeeContent entries are created for all course contents with a 'pending' status.
    Validates automatic status creation on course enrollment.
    """
    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    db_session.add(manager)

    user_role = UserRole(user=manager, role=UserRoleEnum.manager)
    db_session.add(user_role)

    db_session.flush()

    course = Course(title='title', manager_id=manager.id, is_produced=True)
    task = Task(question='question', answer='answer')
    theory = Theory(text='text')
    db_session.add_all([course, task, theory])

    db_session.flush()

    content1 = Content(title='title', course_id=course.id, task_id=task.id, theory_id=None)
    content2 = Content(title='title', course_id=course.id, task_id=None, theory_id=theory.id)
    db_session.add_all([content1, content2])

    db_session.flush()

    employee = User(email='employee@example.com', hashed_password='hash', is_active=True)
    db_session.add(employee)

    user_role = UserRole(user=employee, role=UserRoleEnum.employee)
    db_session.add(user_role)

    db_session.flush()

    course_employee = CourseEmployee(course_id=course.id, employee_id=employee.id)
    db_session.add(course_employee)

    db_session.commit()

    statuses = db_session.query(CourseEmployeeContent).filter_by(course_employee_id=course_employee.id).all()
    assert len(statuses) == 2
    assert all(s.status == ContentStatusEnum.pending for s in statuses)
