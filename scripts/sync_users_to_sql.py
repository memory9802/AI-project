#!/usr/bin/env python3
"""
自動同步 users 表資料到 00_init_with_data.sql
將資料庫中的所有用戶資料匯出並更新到 SQL 初始化檔案中
"""

import pymysql
import os
from datetime import datetime

# 資料庫連線設定
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rootpassword',
    'database': 'outfit_db',
    'charset': 'utf8mb4'
}

# SQL 檔案路徑
SQL_FILE_PATH = '/Users/wenyinkai/Downloads/AI-project-1202MVP/init/00_init_with_data.sql'

def get_all_users():
    """從資料庫取得所有用戶資料"""
    conn = pymysql.connect(**DB_CONFIG)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, password_hash, favorite_style, created_at 
                FROM users 
                ORDER BY id
            """)
            return cursor.fetchall()
    finally:
        conn.close()

def format_user_data(users):
    """格式化用戶資料為 SQL INSERT 語句"""
    if not users:
        return ""
    
    values = []
    for user in users:
        id, username, email, password_hash, favorite_style, created_at = user
        # 格式化時間
        created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else 'NULL'
        # 處理 NULL 值
        favorite_style = favorite_style if favorite_style else ''
        
        value = f"({id},'{username}','{email}','{password_hash}','{favorite_style}','{created_at_str}')"
        values.append(value)
    
    return ','.join(values)

def update_sql_file(users_insert_statement):
    """更新 SQL 檔案中的 users 表資料"""
    # 讀取原始 SQL 檔案
    with open(SQL_FILE_PATH, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到 users 表的 INSERT 語句位置
    start_marker = "LOCK TABLES `users` WRITE;\n/*!40000 ALTER TABLE `users` DISABLE KEYS */;\n"
    end_marker = ";\n/*!40000 ALTER TABLE `users` ENABLE KEYS */;\nUNLOCK TABLES;"
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    
    if start_idx == -1 or end_idx == -1:
        print("❌ 找不到 users 表的 INSERT 語句位置")
        return False
    
    # 建立新的 INSERT 語句
    new_insert = f"{start_marker}INSERT INTO `users` VALUES {users_insert_statement}{end_marker}"
    
    # 替換內容
    before = content[:start_idx]
    after = content[end_idx + len(end_marker):]
    new_content = before + new_insert + after
    
    # 寫入檔案
    with open(SQL_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True

def main():
    """主程式"""
    print("=" * 60)
    print("🔄 開始同步 users 表資料到 SQL 檔案")
    print("=" * 60)
    
    try:
        # 1. 從資料庫取得所有用戶
        print("\n📥 正在從資料庫讀取用戶資料...")
        users = get_all_users()
        print(f"✅ 成功讀取 {len(users)} 筆用戶資料")
        
        # 2. 格式化為 SQL INSERT 語句
        print("\n🔨 正在格式化資料...")
        users_insert = format_user_data(users)
        
        # 3. 更新 SQL 檔案
        print(f"\n📝 正在更新 SQL 檔案: {SQL_FILE_PATH}")
        if update_sql_file(users_insert):
            print("✅ SQL 檔案更新成功！")
            print(f"\n📊 統計:")
            print(f"   - 總用戶數: {len(users)}")
            print(f"   - 更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print("❌ SQL 檔案更新失敗")
            return 1
        
        print("\n" + "=" * 60)
        print("✨ 同步完成！")
        print("=" * 60)
        return 0
        
    except pymysql.Error as e:
        print(f"\n❌ 資料庫錯誤: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
