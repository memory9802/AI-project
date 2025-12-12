"""数据库连接模块"""
import pymysql
import os
from contextlib import contextmanager

def get_db_connection():
    """获取数据库连接"""
    # 支援兩種模式:
    # 1. Docker 容器內: host='mysql'
    # 2. 本機運行: host='localhost' 或 '127.0.0.1'
    db_host = os.environ.get('DB_HOST', 'localhost')
    
    return pymysql.connect(
        host=db_host,
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
