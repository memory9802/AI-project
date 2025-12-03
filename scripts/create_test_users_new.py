#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創建測試用戶腳本 - 每個用戶有不同的密碼
"""
import os
import sys
import bcrypt
import pymysql

# 資料庫配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'rootpassword'),
    'database': os.getenv('DB_NAME', 'outfit_db'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def hash_password(password):
    """生成 bcrypt 密碼雜湊"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_test_users():
    """創建測試用戶"""
    # 測試用戶列表 - 每個用戶有不同的密碼
    test_users = [
        {
            'username': 'testuser1',
            'email': 'test1@example.com',
            'password': 'password123',  # test1 保持原密碼
            'favorite_style': '休閒風格'
        },
        {
            'username': 'testuser2',
            'email': 'test2@example.com',
            'password': 'test2pass',    # test2 新密碼
            'favorite_style': '運動風格'
        },
        {
            'username': 'testuser3',
            'email': 'test3@example.com',
            'password': 'test3pass',    # test3 新密碼
            'favorite_style': '正式風格'
        },
        {
            'username': 'testuser4',
            'email': 'test4@example.com',
            'password': 'test4pass',    # test4 新密碼
            'favorite_style': '街頭風格'
        },
        {
            'username': 'testuser5',
            'email': 'test5@example.com',
            'password': 'test5pass',    # test5 新密碼
            'favorite_style': '優雅風格'
        }
    ]
    
    print("\n" + "="*60)
    print("創建測試用戶")
    print("="*60 + "\n")
    
    try:
        # 連接到資料庫
        print("📡 正在連接到資料庫...")
        connection = pymysql.connect(**DB_CONFIG)
        print("✅ 資料庫連接成功！\n")
        
        with connection.cursor() as cursor:
            created_count = 0
            
            for user in test_users:
                username = user['username']
                email = user['email']
                password = user['password']
                favorite_style = user['favorite_style']
                
                print(f"🔄 創建用戶: {username} ({email})")
                print(f"   密碼: {password}")
                print(f"   風格: {favorite_style}")
                
                # 檢查用戶是否已存在
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                existing = cursor.fetchone()
                
                if existing:
                    print(f"   ⚠️  用戶已存在，跳過\n")
                    continue
                
                # 生成密碼雜湊
                password_hash = hash_password(password)
                
                # 插入用戶
                sql = """
                    INSERT INTO users (username, email, password_hash, favorite_style, created_at) 
                    VALUES (%s, %s, %s, %s, NOW())
                """
                cursor.execute(sql, (username, email, password_hash, favorite_style))
                print(f"   ✅ 創建成功！\n")
                created_count += 1
            
            # 提交更改
            connection.commit()
            
            print("="*60)
            print(f"✅ 完成！成功創建 {created_count}/{len(test_users)} 個測試用戶")
            print("="*60)
            
            # 顯示登入信息
            print("\n📝 測試用戶登入信息：")
            print("-"*60)
            for user in test_users:
                print(f"帳號: {user['email']:<25} 密碼: {user['password']}")
            print("-"*60 + "\n")
        
    except pymysql.Error as e:
        print(f"❌ 資料庫錯誤: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        sys.exit(1)
    finally:
        if 'connection' in locals():
            connection.close()
            print("📡 資料庫連接已關閉")

if __name__ == '__main__':
    create_test_users()
