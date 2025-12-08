#!/usr/bin/env python3
"""
修正 00_init_with_data.sql 的 INSERT 語句欄位對應
舊格式（15 欄位）: id, name, category, color, size, price, image_url, description, created_at, sku, gender, clothing_type, length, price_text, source
新格式（12 欄位）: id, name, category, color, image_url, created_at, sku, gender, clothing_type, length, price, source

需要：
1. 移除 size (index 4)
2. 移除 description (index 7)
3. 將 price_text (index 13) 轉換為數字並移到 price 位置 (index 10)
"""

import re
import sys

def convert_price_text_to_decimal(price_text):
    """將價格文字轉換為數字"""
    if not price_text or price_text == 'NULL':
        return 'NULL'
    
    # 移除貨幣符號和空格
    price = price_text.strip("'").replace('NT$', '').replace('$', '').replace(',', '').strip()
    
    if not price:
        return 'NULL'
    
    try:
        # 轉換為浮點數並格式化為 2 位小數
        return f"{float(price):.2f}"
    except ValueError:
        return 'NULL'

def fix_insert_line(line):
    """修正一行 INSERT 語句"""
    if not line.startswith('INSERT INTO `items` VALUES'):
        return line
    
    # 找到 VALUES 後面的部分
    match = re.match(r'(INSERT INTO `items` VALUES\s+)(.*)', line)
    if not match:
        return line
    
    prefix = match.group(1)
    values_part = match.group(2)
    
    # 分割成多個記錄 (每個記錄由括號包圍)
    records = []
    current_record = []
    paren_count = 0
    in_quotes = False
    escape_next = False
    
    for char in values_part:
        if escape_next:
            current_record.append(char)
            escape_next = False
            continue
            
        if char == '\\':
            escape_next = True
            current_record.append(char)
            continue
            
        if char == "'" and not escape_next:
            in_quotes = not in_quotes
            
        if not in_quotes:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
                if paren_count == 0:
                    current_record.append(char)
                    records.append(''.join(current_record))
                    current_record = []
                    continue
        
        current_record.append(char)
    
    # 轉換每個記錄
    new_records = []
    for record in records:
        record = record.strip().strip(',')
        if not record.startswith('(') or not record.endswith(')'):
            continue
            
        # 移除括號
        record_content = record[1:-1]
        
        # 分割欄位（處理引號內的逗號）
        fields = []
        current_field = []
        in_quotes = False
        escape_next = False
        
        for char in record_content:
            if escape_next:
                current_field.append(char)
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                current_field.append(char)
                continue
                
            if char == "'" and not escape_next:
                in_quotes = not in_quotes
                
            if char == ',' and not in_quotes:
                fields.append(''.join(current_field).strip())
                current_field = []
            else:
                current_field.append(char)
        
        # 加入最後一個欄位
        if current_field:
            fields.append(''.join(current_field).strip())
        
        # 如果不是 15 個欄位，跳過（可能已經轉換過或格式不對）
        if len(fields) != 15:
            new_records.append(record)
            continue
        
        # 轉換欄位順序
        # 舊: [0]id, [1]name, [2]category, [3]color, [4]size, [5]price, [6]image_url, [7]description, 
        #     [8]created_at, [9]sku, [10]gender, [11]clothing_type, [12]length, [13]price_text, [14]source
        # 新: [0]id, [1]name, [2]category, [3]color, [4]image_url, [5]created_at, 
        #     [6]sku, [7]gender, [8]clothing_type, [9]length, [10]price, [11]source
        
        price = convert_price_text_to_decimal(fields[13])  # 使用 price_text 轉換為 price
        
        new_fields = [
            fields[0],   # id
            fields[1],   # name
            fields[2],   # category
            fields[3],   # color
            fields[6],   # image_url
            fields[8],   # created_at
            fields[9],   # sku
            fields[10],  # gender
            fields[11],  # clothing_type
            fields[12],  # length
            price,       # price (from price_text)
            fields[14],  # source
        ]
        
        new_record = '(' + ','.join(new_fields) + ')'
        new_records.append(new_record)
    
    return prefix + ','.join(new_records) + ';\n'

def main():
    input_file = '/Users/liaoyiting/Desktop/stylerec/init/00_init_with_data.sql'
    output_file = '/Users/liaoyiting/Desktop/stylerec/init/00_init_with_data_fixed.sql'
    
    print(f"讀取檔案: {input_file}")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"總共 {len(lines)} 行")
    
    fixed_lines = []
    insert_count = 0
    
    for i, line in enumerate(lines, 1):
        if 'INSERT INTO `items` VALUES' in line:
            insert_count += 1
            print(f"處理第 {i} 行的 INSERT 語句 (共第 {insert_count} 個)")
            fixed_line = fix_insert_line(line)
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    
    print(f"\n共處理 {insert_count} 個 INSERT 語句")
    print(f"寫入檔案: {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print("✅ 完成！")
    print(f"\n請檢查新檔案: {output_file}")
    print("如果正確，請執行:")
    print(f"  mv {output_file} {input_file}")

if __name__ == '__main__':
    main()
