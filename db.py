import os

from dotenv import load_dotenv
from sqlalchemy import create_engine


def get_db_url():
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'config', '.env.db'))
    pg_vars = ['PG_HOST', 'PG_PORT', 'PG_USER', 'PG_PASSWORD', 'PG_DBNAME']
    credentials = {pg_var: os.environ.get(pg_var) for pg_var in pg_vars}
    return 'postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DBNAME}'.format(
        **credentials,
    )


engine = create_engine(get_db_url(), echo=False)
