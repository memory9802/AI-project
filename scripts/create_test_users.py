#!/usr/bin/env python3
"""
測試用戶生成腳本
用於快速創建測試帳號並插入資料庫
"""

import bcrypt
import pymysql
import os
from datetime import datetime

# 資料庫設定
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASS', 'rootpassword'),
    'database': os.getenv('DB_NAME', 'outfit_db'),
    'charset': 'utf8mb4'
}

# 測試用戶資料
TEST_USERS = [
    {
        'username': 'testuser1',
        'email': 'test1@example.com',
        'password': 'password123',
        'favorite_style': '休閒'
    },
    {
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password': 'password123',
        'favorite_style': '正式'
    },
    {
        'username': 'testuser3',
        'email': 'test3@example.com',
        'password': 'password123',
        'favorite_style': '運動'
    },
    {
        'username': 'testuser4',
        'email': 'test4@example.com',
        'password': 'password123',
        'favorite_style': '街頭'
    },
    {
        'username': 'testuser5',
        'email': 'test5@example.com',
        'password': 'password123',
        'favorite_style': '韓風'
    }
]

def hash_password(password: str) -> str:
    """使用 bcrypt 加密密碼"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_test_users():
    """創建測試用戶"""
    try:
        # 連接資料庫
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("🔗 連接資料庫成功")
        print(f"📍 資料庫: {DB_CONFIG['database']} @ {DB_CONFIG['host']}")
        print("-" * 60)
        
        success_count = 0
        skip_count = 0
        
        for user in TEST_USERS:
            try:
                # 檢查用戶是否已存在
                cursor.execute(
                    "SELECT id FROM users WHERE email = %s OR username = %s",
                    (user['email'], user['username'])
                )
                
                if cursor.fetchone():
                    print(f"⚠️  用戶已存在: {user['username']} ({user['email']})")
                    skip_count += 1
                    continue
                
                # 加密密碼
                password_hash = hash_password(user['password'])
                
                # 插入用戶
                cursor.execute(
                    """
                    INSERT INTO users (username, email, password_hash, favorite_style)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (user['username'], user['email'], password_hash, user['favorite_style'])
                )
                
                print(f"✅ 創建成功: {user['username']} ({user['email']})")
                success_count += 1
                
            except Exception as e:
                print(f"❌ 創建失敗: {user['username']} - {str(e)}")
        
        # 提交事務
        conn.commit()
        
        print("-" * 60)
        print(f"📊 統計結果:")
        print(f"   - 成功創建: {success_count} 個用戶")
        print(f"   - 已存在跳過: {skip_count} 個用戶")
        print(f"   - 總計: {len(TEST_USERS)} 個用戶")
        
        # 查詢並顯示所有測試用戶
        cursor.execute(
            """
            SELECT username, email, favorite_style, created_at
            FROM users
            WHERE username IN ('testuser1', 'testuser2', 'testuser3', 'testuser4', 'testuser5')
            ORDER BY username
            """
        )
        
        users = cursor.fetchall()
        
        if users:
            print("\n" + "=" * 60)
            print("📋 測試帳號列表（密碼統一為: password123）")
            print("=" * 60)
            print(f"{'用戶名':<15} {'電子郵件':<25} {'風格':<10}")
            print("-" * 60)
            
            for user in users:
                print(f"{user[0]:<15} {user[1]:<25} {user[2]:<10}")
            
            print("=" * 60)
        
        cursor.close()
        conn.close()
        
        print("\n✨ 完成！")
        
    except pymysql.Error as e:
        print(f"❌ 資料庫錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 未知錯誤: {e}")
        return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 測試用戶生成工具")
    print("=" * 60)
    print()
    
    create_test_users()
