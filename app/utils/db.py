import psycopg2
from psycopg2.extras import DictCursor


def connect(dsn):
    """
    Convenience connection function that returns both the connection and cursor
    object, with which we can make queries.
    """
    conn = psycopg2.connect(dsn=dsn)
    cur = conn.cursor(cursor_factory=DictCursor)
    return conn, cur


def dict2str(d):
    res = ""
    for k, v in d.items():
        res += f"{k} = {v} \n"
    return res


def update(cur, table: str, id: int, data: dict):
    """
    Convenience function that updates a PostgreSQL database with data.

    We build the query statement based on the data passed into it. The data
    should be a dictionary where the keys are column names, and values are the
    data to be updated.

    Does NOT return anything.

    :param cur: psycopg2 cursor object
    :param table: The table to update
    :param id: The row to update
    :param data: Data to update
    """
    query = f"""UPDATE {table}
    SET
    {dict2str(data)}
    WHERE
    id={id}
    """
    cur.execute(query)
