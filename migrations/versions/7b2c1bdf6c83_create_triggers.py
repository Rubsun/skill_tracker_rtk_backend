"""Create triggers

Revision ID: 7b2c1bdf6c83
Revises: c6d41c8fda3c
Create Date: 2025-06-02 10:44:21.931821

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = '7b2c1bdf6c83'
down_revision: Union[str, None] = 'c6d41c8fda3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    triggers_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', 'triggers')
    for filename in sorted(os.listdir(triggers_path)):
        if filename.endswith('.sql'):
            filepath = os.path.join(triggers_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                sql = f.read()
                op.execute(sql)


def downgrade():
    conn = op.get_bind()

    conn.execute("""
        DROP TRIGGER IF EXISTS trg_check_user_roles ON users;
        DROP TRIGGER IF EXISTS trg_check_content_type_task_theory ON contents;
        DROP TRIGGER IF EXISTS trg_check_course_manager_role ON courses;
        DROP TRIGGER IF EXISTS trg_check_course_employee_role ON course_employees;
        DROP TRIGGER IF EXISTS trg_create_employee_content_statuses ON course_employees;
    """)

    conn.execute("""
        DROP FUNCTION IF EXISTS check_user_roles() CASCADE;
        DROP FUNCTION IF EXISTS check_content_type_task_theory() CASCADE;
        DROP FUNCTION IF EXISTS check_course_manager_role() CASCADE;
        DROP FUNCTION IF EXISTS check_course_employee_role() CASCADE;
        DROP FUNCTION IF EXISTS create_employee_content_statuses() CASCADE;
    """)
