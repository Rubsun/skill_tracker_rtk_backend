from models.models import User, UserRole, Course, Notification, CourseEmployee, Content, Task, Theory, Comment, CourseEmployeeContent
from models.enums import UserRoleEnum


def create_basic_data(db_session):
    manager = User(email='manager@example.com', hashed_password='hash', is_active=True)
    employee = User(email='employee@example.com', hashed_password='hash', is_active=True)
    db_session.add_all([manager, employee])
    db_session.flush()

    db_session.add_all([
        UserRole(user=manager, role=UserRoleEnum.manager),
        UserRole(user=employee, role=UserRoleEnum.employee)
    ])
    db_session.flush()

    course = Course(title="title", manager_id=manager.id, is_produced=True)
    db_session.add(course)
    db_session.flush()

    theory = Theory(text="text")
    task = Task(question="question", answer="answer")

    db_session.add_all([theory, task])
    db_session.flush()

    content1 = Content(course_id=course.id, title="title", theory_id=theory.id)
    content2 = Content(course_id=course.id, title="title", task_id=task.id)

    db_session.add_all([content1, content2])
    db_session.flush()

    course_employee = CourseEmployee(course_id=course.id, employee_id=employee.id)
    db_session.add(course_employee)
    db_session.flush()

    comment = Comment(user_id=employee.id, content_id=content1.id, text="text")
    db_session.add(comment)

    db_session.commit()

    return {
        "manager": manager,
        "employee": employee,
        "course": course,
        "content1": content1,
        "content2": content2,
        "course_employee": course_employee,
        "comment": comment
    }


def test_cascade_delete_user(db_session):
    data = create_basic_data(db_session)

    db_session.delete(data["employee"])
    db_session.commit()

    assert db_session.query(UserRole).filter_by(user_id=data["employee"].id).count() == 0
    assert db_session.query(CourseEmployee).filter_by(employee_id=data["employee"].id).count() == 0
    assert db_session.query(Comment).filter_by(user_id=data["employee"].id).count() == 0
    assert db_session.query(Notification).filter_by(user_id=data["employee"].id).count() == 0
    assert db_session.query(CourseEmployeeContent).join(CourseEmployee).filter(CourseEmployee.employee_id == data["employee"].id).count() == 0


def test_cascade_delete_manager_user_deletes_courses(db_session):
    data = create_basic_data(db_session)

    db_session.delete(data["manager"])
    db_session.commit()

    assert db_session.query(Course).filter_by(manager_id=data["manager"].id).count() == 0
    assert db_session.query(Content).filter_by(course_id=data["course"].id).count() == 0
    assert db_session.query(CourseEmployee).filter_by(course_id=data["course"].id).count() == 0


def test_cascade_delete_course(db_session):
    data = create_basic_data(db_session)

    db_session.delete(data["course"])
    db_session.commit()

    assert db_session.query(Content).filter(Content.course_id == data["course"].id).count() == 0
    assert db_session.query(CourseEmployee).filter(CourseEmployee.course_id == data["course"].id).count() == 0
    assert db_session.query(CourseEmployeeContent).filter_by(content_id=data["content1"].id).count() == 0
    assert db_session.query(Comment).filter_by(content_id=data["content1"].id).count() == 0


def test_cascade_delete_content(db_session):
    data = create_basic_data(db_session)

    db_session.delete(data["content1"])
    db_session.commit()

    assert db_session.query(Comment).filter_by(content_id=data["content1"].id).count() == 0
    assert db_session.query(CourseEmployeeContent).filter_by(content_id=data["content1"].id).count() == 0
    assert db_session.query(Theory).filter_by(id=data["content1"].theory_id).count() == 0
