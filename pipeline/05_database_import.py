"""
資料庫匯入 - 整合版
將最終資料集匯入 MySQL outfit_db 資料庫

輸入: init/gemini_results_only.csv
輸出: 
  - init/outfit_db.sql (完整資料庫初始化腳本)
  - 直接匯入 MySQL (可選)
"""

import pandas as pd
import os


# ==================== SQL 生成 ====================
def map_clothing_type_to_category(clothing_type: str) -> str:
    """
    將服裝類型映射到資料庫的 category ENUM
    
    Args:
        clothing_type: '上衣' or '下身'
        
    Returns:
        'top' or 'bottom'
    """
    mapping = {
        '上衣': 'top',
        '下身': 'bottom'
    }
    return mapping.get(clothing_type, None)


def escape_sql_value(value) -> str:
    """
    SQL 字串轉義
    
    Args:
        value: 任意值
        
    Returns:
        SQL格式的字串（帶引號）或 NULL
    """
    if pd.isna(value) or value == '-' or value == '':
        return 'NULL'
    
    # 轉義單引號
    escaped = str(value).replace("'", "\\'")
    return f"'{escaped}'"


def generate_insert_statements(csv_file: str) -> list:
    """
    從 CSV 生成 INSERT 語句
    
    Args:
        csv_file: CSV檔案路徑
        
    Returns:
        INSERT 語句列表
    """
    df = pd.read_csv(csv_file)
    
    print(f"讀取 {len(df)} 筆資料")
    print(f"欄位: {', '.join(df.columns)}")
    
    statements = []
    
    for idx, row in df.iterrows():
        # 映射 clothing_type → category
        category = map_clothing_type_to_category(row['Gemini clothing_type'])
        
        # 處理各欄位
        sku = escape_sql_value(row['sku'])
        name = escape_sql_value(row['name'][:100] if pd.notna(row['name']) else None)
        gender = escape_sql_value(row['Gemini gender'])
        clothing_type = escape_sql_value(row['Gemini category'][:50] if pd.notna(row['Gemini category']) else None)
        cat = f"'{category}'" if category else 'NULL'
        length = escape_sql_value(row['Gemini length'])
        color = escape_sql_value(row['Gemini color'][:50] if pd.notna(row['Gemini color']) else None)
        price = escape_sql_value(row.get('price', None))
        img = escape_sql_value(row['image_url'])
        
        sql = f"INSERT INTO items (sku, name, gender, clothing_type, category, length, color, price, image_url) VALUES ({sku}, {name}, {gender}, {clothing_type}, {cat}, {length}, {color}, {price}, {img});"
        statements.append(sql)
    
    return statements


def create_full_database_script(insert_statements: list, output_file: str):
    """
    創建完整的資料庫初始化腳本
    
    Args:
        insert_statements: INSERT 語句列表
        output_file: 輸出檔案路徑
    """
    script = f"""-- 初始化穿搭資料庫
CREATE DATABASE IF NOT EXISTS outfit_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE outfit_db;

-- =============================
-- 衣物表 items
-- =============================
CREATE TABLE IF NOT EXISTS items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  sku VARCHAR(50) UNIQUE,
  name VARCHAR(100) NOT NULL,
  gender ENUM('男','女','-') DEFAULT NULL,
  clothing_type VARCHAR(50),
  category ENUM('top','bottom','outer','shoes','accessory') NOT NULL,
  length ENUM('短','長','-') DEFAULT NULL,
  color VARCHAR(50),
  size VARCHAR(10),
  price VARCHAR(20),
  image_url VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- UNIQLO 商品資料（共 {len(insert_statements)} 筆）
-- =============================
{chr(10).join(insert_statements)}

-- =============================
-- 穿搭表 outfits
-- =============================
CREATE TABLE IF NOT EXISTS outfits (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  occasion ENUM('casual','formal','street','sport','date') DEFAULT 'casual',
  description TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================
-- 穿搭與衣物關聯表 outfit_items
-- =============================
CREATE TABLE IF NOT EXISTS outfit_items (
  id INT AUTO_INCREMENT PRIMARY KEY,
  outfit_id INT NOT NULL,
  item_id INT NOT NULL,
  FOREIGN KEY (outfit_id) REFERENCES outfits(id) ON DELETE CASCADE,
  FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
);

-- =============================
-- 標籤表 tags
-- =============================
CREATE TABLE IF NOT EXISTS tags (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) UNIQUE
);

INSERT INTO tags (name) VALUES
('休閒'), ('正式'), ('街頭'), ('運動'), ('約會');

-- =============================
-- 使用者表 users
-- =============================
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  favorite_style VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 預設使用者
INSERT INTO users (username, password, favorite_style)
VALUES
('ian', 'test123', '休閒'),
('guest', '1234', '街頭');

-- =============================
-- 收藏表 user_favorites
-- =============================
CREATE TABLE IF NOT EXISTS user_favorites (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  outfit_id INT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (outfit_id) REFERENCES outfits(id) ON DELETE CASCADE
);

-- =============================
-- 完成訊息
-- =============================
SELECT '✅ Outfit database initialized successfully!' AS status;
SELECT CONCAT('📊 Imported ', COUNT(*), ' items') AS info FROM items;
"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(script)
    
    print(f"✅ SQL 腳本已生成: {output_file}")


def import_to_mysql(sql_file: str, user: str = 'root', password: str = None, host: str = 'localhost'):
    """
    直接匯入 MySQL (需要 pymysql)
    
    Args:
        sql_file: SQL檔案路徑
        user: MySQL使用者名稱
        password: MySQL密碼
        host: MySQL主機
    """
    try:
        import pymysql
    except ImportError:
        print("⚠️  pymysql 未安裝，請手動執行 SQL 檔案")
        print(f"\n執行方式:")
        print(f"  mysql -u {user} -p < {sql_file}")
        return
    
    if password is None:
        import getpass
        password = getpass.getpass("請輸入 MySQL 密碼: ")
    
    try:
        # 連接 MySQL
        conn = pymysql.connect(
            host=host,
            user=user,
            password=password,
            charset='utf8mb4'
        )
        
        cursor = conn.cursor()
        
        # 執行 SQL 檔案
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_commands = f.read().split(';')
        
        for command in sql_commands:
            command = command.strip()
            if command:
                cursor.execute(command)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ 資料已成功匯入 MySQL")
        
    except Exception as e:
        print(f"❌ 匯入失敗: {e}")
        print(f"\n請手動執行:")
        print(f"  mysql -u {user} -p < {sql_file}")


def main():
    """主程式流程"""
    print("=" * 80)
    print("💾 資料庫匯入")
    print("=" * 80)
    
    # 1. 生成 INSERT 語句
    print("\n步驟 1: 從 CSV 生成 INSERT 語句")
    csv_file = 'init/gemini_results_only.csv'
    
    if not os.path.exists(csv_file):
        print(f"❌ 找不到檔案: {csv_file}")
        print("\n請先執行:")
        print("  python pipeline/04_data_processing.py")
        return
    
    insert_statements = generate_insert_statements(csv_file)
    print(f"✅ 生成 {len(insert_statements)} 條 INSERT 語句")
    
    # 顯示前3筆預覽
    print("\n前3筆預覽:")
    for i, stmt in enumerate(insert_statements[:3], 1):
        print(f"\n第{i}筆:")
        print(stmt[:200] + "...")
    
    # 2. 創建完整資料庫腳本
    print("\n步驟 2: 創建完整資料庫腳本")
    output_file = 'init/outfit_db.sql'
    create_full_database_script(insert_statements, output_file)
    
    # 3. 詢問是否直接匯入
    print("\n" + "=" * 80)
    print("資料庫腳本已生成")
    print("=" * 80)
    
    print(f"\n手動匯入方式:")
    print(f"  mysql -u root -p < {output_file}")
    print("\n或在 MySQL 中執行:")
    print(f"  SOURCE {output_file};")
    
    # 可選: 自動匯入
    # response = input("\n是否現在匯入到 MySQL? (y/n): ")
    # if response.lower() == 'y':
    #     import_to_mysql(output_file)


if __name__ == '__main__':
    main()
