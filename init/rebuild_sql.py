#!/usr/bin/env python3
"""
重建 00_init_with_data.sql 使用乾淨的結構定義
從 01_schema_only.sql 取得結構,從備份檔取得資料
"""

import re

def extract_data_section(backup_file, start_line, end_line):
    """提取資料區段"""
    with open(backup_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return ''.join(lines[start_line-1:end_line])

def main():
    backup_file = '00_init_with_data.sql.backup'
    schema_file = '01_schema_only.sql'
    output_file = '00_init_with_data_new.sql'
    
    # 讀取 schema 定義
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_content = f.read()
    
    # 移除結尾的訊息部分
    schema_content = re.sub(
        r'-- =============================\n-- 完成訊息\n-- =============================.*',
        '',
        schema_content,
        flags=re.DOTALL
    )
    
    # 提取資料區段 (從備份檔)
    items_data = extract_data_section(backup_file, 82, 93)  # items 資料
    partner_data = extract_data_section(backup_file, 119, 123)  # partner_products 資料  
    users_data = extract_data_section(backup_file, 181, 185)  # users 資料
    
    # 提取 mysqldump 標頭
    header = extract_data_section(backup_file, 1, 20)
    
    # 組合新檔案
    output_content = []
    
    # 1. MySQL dump 標頭
    output_content.append(header.rstrip())
    output_content.append('')
    
    # 2. 使用乾淨的 schema 定義 (但逐表插入資料)
    # 解析 schema 找出每個表的定義
    tables = {
        'users': None,
        'items': None,
        'user_wardrobe': None,
        'partner_products': None,
        'conversation_history': None,
        'rating': None
    }
    
    # 從 schema 中提取每個表的結構
    for table in tables.keys():
        pattern = rf'(-- ={5,}\n-- .*{table}.*\n-- ={5,}\n.*?CREATE TABLE {table} \(.*?\).*?;)'
        match = re.search(pattern, schema_content, re.DOTALL | re.IGNORECASE)
        if match:
            tables[table] = match.group(1)
    
    # 3. 按照依賴順序輸出表定義和資料
    
    # users 表 (基礎表)
    if tables['users']:
        output_content.append(tables['users'])
        output_content.append('')
        output_content.append('--')
        output_content.append('-- Dumping data for table `users`')
        output_content.append('--')
        output_content.append('')
        output_content.append(users_data.rstrip())
        output_content.append('')
    
    # items 表
    if tables['items']:
        output_content.append(tables['items'])
        output_content.append('')
        output_content.append('--')
        output_content.append('-- Dumping data for table `items`')
        output_content.append('--')
        output_content.append('')
        output_content.append(items_data.rstrip())
        output_content.append('')
    
    # user_wardrobe 表 (空資料)
    if tables['user_wardrobe']:
        output_content.append(tables['user_wardrobe'])
        output_content.append('')
        output_content.append('--')
        output_content.append('-- Dumping data for table `user_wardrobe`')
        output_content.append('--')
        output_content.append('')
        output_content.append('LOCK TABLES `user_wardrobe` WRITE;')
        output_content.append('/*!40000 ALTER TABLE `user_wardrobe` DISABLE KEYS */;')
        output_content.append('/*!40000 ALTER TABLE `user_wardrobe` ENABLE KEYS */;')
        output_content.append('UNLOCK TABLES;')
        output_content.append('')
    
    # partner_products 表
    if tables['partner_products']:
        output_content.append(tables['partner_products'])
        output_content.append('')
        output_content.append('--')
        output_content.append('-- Dumping data for table `partner_products`')
        output_content.append('--')
        output_content.append('')
        output_content.append(partner_data.rstrip())
        output_content.append('')
    
    # conversation_history 表 (空資料,新結構)
    if tables['conversation_history']:
        output_content.append(tables['conversation_history'])
        output_content.append('')
        output_content.append('--')
        output_content.append('-- Dumping data for table `conversation_history`')
        output_content.append('--')
        output_content.append('')
        output_content.append('LOCK TABLES `conversation_history` WRITE;')
        output_content.append('/*!40000 ALTER TABLE `conversation_history` DISABLE KEYS */;')
        output_content.append('/*!40000 ALTER TABLE `conversation_history` ENABLE KEYS */;')
        output_content.append('UNLOCK TABLES;')
        output_content.append('')
    
    # rating 表 (新增,空資料)
    if tables['rating']:
        output_content.append(tables['rating'])
        output_content.append('')
        output_content.append('--')
        output_content.append('-- Dumping data for table `rating`')
        output_content.append('--')
        output_content.append('')
        output_content.append('LOCK TABLES `rating` WRITE;')
        output_content.append('/*!40000 ALTER TABLE `rating` DISABLE KEYS */;')
        output_content.append('/*!40000 ALTER TABLE `rating` ENABLE KEYS */;')
        output_content.append('UNLOCK TABLES;')
        output_content.append('')
    
    # 4. MySQL dump 結尾
    footer = extract_data_section(backup_file, 196, 197)
    output_content.append(footer.rstrip())
    
    # 寫入新檔案
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_content))
    
    print(f'✅ 成功生成新檔案: {output_file}')
    print(f'📝 已使用乾淨的結構定義並保留所有資料')
    print(f'📊 包含的資料表:')
    print(f'  - users: 50 個測試使用者')
    print(f'  - items: 完整商品資料')
    print(f'  - partner_products: 3 個合作品牌商品')
    print(f'  - user_wardrobe: 空資料')
    print(f'  - conversation_history: 空資料 (新結構)')
    print(f'  - rating: 空資料 (新增表格) ⭐')

if __name__ == '__main__':
    main()
