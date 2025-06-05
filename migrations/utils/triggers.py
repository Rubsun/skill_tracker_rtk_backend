import os
import re
from alembic import op
from sqlalchemy import text


def apply_sql_files_from_directory(directory_path: str) -> None:
    if not os.path.isdir(directory_path):
        raise Exception(f"Directory not found: {directory_path}")

    for filename in sorted(os.listdir(directory_path)):
        if filename.endswith('.sql'):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                sql = f.read()
                op.execute(sql)


def drop_triggers_and_functions_from_directory(directory_path: str) -> None:
    if not os.path.isdir(directory_path):
        raise Exception(f"Directory not found: {directory_path}")

    conn = op.get_bind()
    drop_triggers = []
    drop_functions = []

    for filename in os.listdir(directory_path):
        if filename.endswith('.sql'):
            filepath = os.path.join(directory_path, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                sql = f.read()

                for match in re.findall(r'CREATE\s+TRIGGER\s+(\w+)\s+.*?ON\s+(\w+)', sql, re.IGNORECASE | re.DOTALL):
                    trigger_name, table_name = match
                    drop_triggers.append(f'DROP TRIGGER IF EXISTS {trigger_name} ON {table_name};')

                for match in re.findall(r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(\w+)\s*\(', sql, re.IGNORECASE):
                    function_name = match
                    drop_functions.append(f'DROP FUNCTION IF EXISTS {function_name}() CASCADE;')

    for stmt in drop_triggers:
        conn.execute(text(stmt))

    for stmt in drop_functions:
        conn.execute(text(stmt))
