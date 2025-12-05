"""数据库连接模块"""
import pymysql
from contextlib import contextmanager

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host='mysql',
        user='root',
        password='rootpassword',
        database='outfit_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False
    )

@contextmanager
def get_db_cursor():
    """数据库游标上下文管理器"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
