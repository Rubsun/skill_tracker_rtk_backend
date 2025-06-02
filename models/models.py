from uuid import UUID, uuid4
from typing import List
from sqlalchemy import (
    String, ForeignKey, Text, DateTime, Enum, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone

from .meta import Base
from .enums import UserRoleEnum, ContentStatusEnum


class User(Base):
    """
    The model for users in the system.

    Attributes:
        id (UUID): The unique identifier for the user (primary key).
        given_name (str): The user's first name, non-null, max 50 chars.
        family_name (str): The user's last name, non-null, max 100 chars.
        username (str): The user's unique username, non-null, max 100 chars.
        password_hash (str): The hashed password of the user, non-null, max 255 chars.

    Relationships:
        roles (List[UserRole]): A relationship with the UserRole model, indicating the roles assigned to the user.
        manager_courses (List[Course]): A relationship with the Course model, indicating the courses managed by the user.
        employee_courses (List[CourseEmployee]): A relationship with the CourseEmployee model, indicating the courses assigned to the user.
        comments (List[Comment]): A relationship with the Comment model, indicating the comments made by the user.
    """
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    given_name: Mapped[str] = mapped_column(String(50), nullable=False)
    family_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    roles: Mapped[List['UserRole']] = relationship('UserRole', back_populates='user', cascade="all, delete-orphan")
    manager_courses: Mapped[List['Course']] = relationship('Course', back_populates='manager', cascade="all, delete-orphan")
    employee_courses: Mapped[List['CourseEmployee']] = relationship('CourseEmployee', back_populates='employee', cascade="all, delete-orphan")
    comments: Mapped[List['Comment']] = relationship('Comment', back_populates='user', cascade="all, delete-orphan")


class UserRole(Base):
    """
    The model for the association between users and their roles in the system.

    Attributes:
        id (UUID): The unique identifier for the user role record (primary key).
        role (UserRoleEnum): The role of the user, which can be 'manager' or 'employee'.
        user_id (UUID): A foreign key referencing the users table, indicating the user to whom this role is assigned.

    Relationships:
        user (User): A relationship with the user to whom this role belongs.
    """
    __tablename__ = 'user_roles'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    role: Mapped[UserRoleEnum] = mapped_column(Enum(UserRoleEnum), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    
    user: Mapped['User'] = relationship('User', back_populates='roles')


class Course(Base):
    """
    The model for courses in the system.

    Attributes:
        id (UUID): The unique identifier for the course (primary key).
        title (str): The title of the course, non-null, max 200 chars.
        description (str): The description of the course, optional.
        deadline (datetime): The deadline for the course, optional.
        created_at (datetime): The timestamp when the course was created, non-null.
        manager_id (UUID): A foreign key referencing the users table, indicating the manager responsible for the course. 

    Relationships:
        manager (User): A relationship with the User model, indicating the manager of the course.
        contents (List[Content]): A relationship with the Content model, indicating the contents of the course.
        course_employees ([List[CourseEmployee]): A relationship with the CourseEmployee model.
    """
    __tablename__ = 'courses'
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    manager_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    manager: Mapped['User'] = relationship('User', back_populates='manager_courses')
    contents: Mapped[List['Content']] = relationship('Content', back_populates='course', cascade="all, delete-orphan")
    course_employees: Mapped[List['CourseEmployee']] = relationship('CourseEmployee', back_populates='course')


class CourseEmployee(Base):
    """
    The model for the association between users (employees) and courses.

    Attributes:
        id (UUID): The unique identifier for the course employee record (primary key).
        assigned_at (datetime): The timestamp when the employee was assigned to the course.
        course_id (UUID): A foreign key referencing the courses table, indicating the course the employee is assigned to.
        employee_id (UUID): A foreign key referencing the users table, indicating the employee.

    Relationships:
        course (Course): A relationship with the Course model, indicating the course the employee is associated with.
        employee (User): A relationship with the User model, indicating the employee assigned to the course.
        content_statuses (List[EmployeeContentStatus]): A relationship with EmployeeContentStatus, representing the statuses of course contents for this particular employee.
    """
    __tablename__ = 'course_employees'

    __table_args__ = (
        UniqueConstraint('course_id', 'employee_id', name='uq_course_employee'),
    )

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    course_id: Mapped[UUID] = mapped_column(ForeignKey('courses.id', ondelete="CASCADE"))
    employee_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"))

    course: Mapped['Course'] = relationship('Course', back_populates="course_employees")
    employee: Mapped['User'] = relationship('User', back_populates="employee_courses")
    content_statuses: Mapped[List['EmployeeContentStatus']] = relationship('EmployeeContentStatus', back_populates='course_employee', cascade="all, delete-orphan")


class Content(Base):
    """
    Course content model (task, theory). This model can store both tasks and theory associated with a course.

    Attributes:
        id (UUID): The unique identifier for the course content record (primary key).
        title (str): The title of the theory, non-null, max 200 chars.
        deadline (datetime): The deadline for the task (if the content is a task).
        created_at (datetime): The timestamp when the course content record was created.
        course_id (UUID): A foreign key referencing the courses table, indicating which course this content belongs to.
        task_id (UUID): A foreign key referencing the tasks table, indicating that this content is related to a task (if it's a task).
        theory_id (UUID): A foreign key referencing the theories table, indicating that this content is related to a theory.

    Relationships:
        course (Course): A relationship with the Course model, indicating the course to which this content belongs.
        task (Task): A relationship with the Task model, indicating that this content represents a task.
        theory (Theory): A relationship with the Theory model, indicating that this content represents a theory.
        comments (List[Comment]): A relationship with the Comment model, indicating the comments made on this course content.
        content_statuses (List[EmployeeContentStatus]): A relationship with EmployeeContentStatus, representing the statuses of this content for each employee assigned to the course.
    """
    __tablename__ = 'contents'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    course_id: Mapped[UUID] = mapped_column(ForeignKey('courses.id', ondelete="CASCADE"))
    task_id: Mapped[UUID] = mapped_column(ForeignKey('tasks.id', ondelete="CASCADE"), nullable=True)
    theory_id: Mapped[UUID] = mapped_column(ForeignKey('theories.id', ondelete="CASCADE"), nullable=True)
    
    course: Mapped['Course'] = relationship('Course', back_populates='contents')
    task: Mapped['Task'] = relationship('Task', back_populates='contents', uselist=False)
    theory: Mapped['Theory'] = relationship('Theory', back_populates='contents', uselist=False)
    comments: Mapped[List['Comment']] = relationship('Comment', back_populates='content', cascade="all, delete-orphan")
    content_statuses: Mapped[List['EmployeeContentStatus']] = relationship('EmployeeContentStatus', back_populates='content', cascade="all, delete-orphan")


class EmployeeContentStatus(Base):
    """
    Represents the status of a specific content item (task or theory) for a given
    course employee (user enrolled in a course).

    This model tracks the progress of an employee on individual course contents,
    allowing different statuses such as 'pending', 'done', or 'incorrect' depending
    on the content type.

    Attributes:
        id (UUID): Unique identifier for the status record (primary key).
        course_employee_id (UUID): Foreign key linking to the CourseEmployee record, indicating which user-course enrollment this status belongs to.
        content_id (UUID): Foreign key linking to the Content record, indicating the specific content item whose status is tracked.
        status (ContentStatusEnum): Current status of the content for this employee. Typical values include 'pending', 'done', and 'incorrect' (for tasks).
        updated_at (datetime): Timestamp of the last update to this status record, stored with timezone awareness.

    Relationships:
        course_employee (CourseEmployee): The enrollment of the user in the course.
        content (Content): The course content item (task or theory) being tracked.
    """
    __tablename__ = 'employee_content_statuses'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    course_employee_id: Mapped[UUID] = mapped_column(ForeignKey('course_employees.id'), nullable=False)
    content_id: Mapped[UUID] = mapped_column(ForeignKey('contents.id'), nullable=False)
    status: Mapped[ContentStatusEnum] = mapped_column(Enum(ContentStatusEnum), nullable=False, default=ContentStatusEnum.pending)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    course_employee: Mapped['CourseEmployee'] = relationship('CourseEmployee', back_populates='content_statuses')
    content: Mapped['Content'] = relationship('Content', back_populates='content_statuses')


class Task(Base):
    """
    The model for tasks within a course.

    Attributes:
        id (UUID): The unique identifier for the task (primary key).
        question (str): The question or prompt for the task, non-null, max 200 chars.
        answer (str): The answer for the task, non-null, max 200 chars.

    Relationships:
        contents (List[Content]): A relationship with the Content model, indicating that the task is part of a course's content.
    """
    __tablename__ = 'tasks'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    question: Mapped[str] = mapped_column(String(200), nullable=False)
    answer: Mapped[str] = mapped_column(String(200), nullable=False)
    
    contents: Mapped[List['Content']] = relationship('Content', back_populates='task')


class Theory(Base):
    """
    The model for theoretical content within a course.

    Attributes:
        id (UUID): The unique identifier for the theory (primary key).
        text (str): The text of the theory, non-null.

    Relationships:
        contents (List[Content]): A relationship with the Content model, indicating that the theory is part of a course's content.
    """
    __tablename__ = 'theories'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    contents: Mapped[List['Content']] = relationship('Content', back_populates='theory')


class Comment(Base):
    """
    The model for comments on course content (tasks or theories).

    Attributes:
        id (UUID): The unique identifier for the comment (primary key).
        text (str): The text of the comment, non-null.
        created_at (datetime): The timestamp when the comment was created.
        content_id (UUID): A foreign key referencing the contents table, indicating which content the comment belongs to.
        user_id (UUID): A foreign key referencing the users table, indicating the user who wrote the comment.

    Relationships:
        content (Content): A relationship with the Content model, indicating which content the comment is associated with.
        user (User): A relationship with the User model, indicating the user who wrote the comment.
    """
    __tablename__ = 'comments'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    content_id: Mapped[UUID] = mapped_column(ForeignKey('contents.id', ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete="CASCADE"), nullable=False)

    content: Mapped['Content'] = relationship('Content', back_populates='comments')
    user: Mapped['User'] = relationship('User', back_populates='comments')
