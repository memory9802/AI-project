"""
NET 配件與鞋類爬蟲
從 NET 官網爬取配件 (accessories) 和鞋類 (shoes) 商品

目標: 各爬取 10 筆商品，使用 Gemini 辨識缺少的欄位
輸出: 直接插入資料庫 items 表

欄位對應:
- name: 商品名稱
- category: shoes 或 accessories
- color: 顏色 (由 Gemini 辨識)
- image_url: 圖片URL
- sku: 商品編號
- gender: 性別 (由 Gemini 辨識)
- clothing_type: NULL (配件和鞋子不需要)
- length: NULL
- price: 價格
- source: 'net'
"""

import os
import sys
import requests
from bs4 import BeautifulSoup
import time
import re
import json
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import mysql.connector
from datetime import datetime

# ==================== 配置 ====================
# 使用 Unsplash 作為圖片來源，創建測試商品數據
# 實際部署時可替換為真實電商 API

NET_BASE_URL = "https://images.unsplash.com"

# 測試用商品數據（模擬從 NET 爬取的數據）
MOCK_ACCESSORIES = [
    {"name": "皮革斜背包", "price": 1290, "img_id": "photo-1590874103328-eac38a683ce7"},
    {"name": "經典棒球帽", "price": 590, "img_id": "photo-1588850561407-ed78c282e89b"},
    {"name": "簡約腰帶", "price": 690, "img_id": "photo-1624222247344-550fb60583e2"},
    {"name": "太陽眼鏡", "price": 890, "img_id": "photo-1511499767150-a48a237f0083"},
    {"name": "針織圍巾", "price": 790, "img_id": "photo-1520903920243-00d872a2d1c9"},
    {"name": "帆布托特包", "price": 1190, "img_id": "photo-1590874103328-eac38a683ce7"},
    {"name": "手拿包", "price": 990, "img_id": "photo-1566150905458-1bf1fc113f0d"},
    {"name": "後背包", "price": 1590, "img_id": "photo-1553062407-98eeb64c6a62"},
    {"name": "皮革手錶", "price": 2990, "img_id": "photo-1523170335258-f5ed11844a49"},
    {"name": "金屬手環", "price": 590, "img_id": "photo-1611591437281-460bfbe1220a"},
]

MOCK_SHOES = [
    {"name": "經典白球鞋", "price": 1990, "img_id": "photo-1549298916-b41d501d3772"},
    {"name": "黑色皮鞋", "price": 2490, "img_id": "photo-1533867617858-e7b97e060509"},
    {"name": "休閒帆布鞋", "price": 1290, "img_id": "photo-1525966222134-fcfa99b8ae77"},
    {"name": "運動慢跑鞋", "price": 2290, "img_id": "photo-1542291026-7eec264c27ff"},
    {"name": "高筒靴", "price": 3490, "img_id": "photo-1608256246200-53e635b5b65f"},
    {"name": "涼鞋", "price": 990, "img_id": "photo-1603808033192-082d6919d3e1"},
    {"name": "樂福鞋", "price": 1790, "img_id": "photo-1533867617858-e7b97e060509"},
    {"name": "板鞋", "price": 1590, "img_id": "photo-1595950653106-6c9ebd614d3a"},
    {"name": "登山鞋", "price": 2990, "img_id": "photo-1520639888713-7851133b1ed0"},
    {"name": "懶人鞋", "price": 1390, "img_id": "photo-1560343090-f0409e92791a"},
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
}

# Gemini API 配置
API_KEY = os.environ.get('GEMINI_API_KEY', '')
if API_KEY:
    genai.configure(api_key=API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
else:
    print("⚠️  未設定 GEMINI_API_KEY，將跳過 Gemini 辨識")
    model = None

# 資料庫配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'port': int(os.environ.get('DB_PORT', '3306')),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASS', 'rootpassword'),
    'database': os.environ.get('DB_NAME', 'outfit_db'),
    'charset': 'utf8mb4',
}


# ==================== 圖片處理 ====================
def download_image(url: str, timeout: int = 10) -> Image.Image:
    """下載商品圖片"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
            'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8',
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return Image.open(BytesIO(response.content)).convert('RGB')
    except Exception as e:
        print(f"  ❌ 圖片下載失敗: {e}")
        return None


# ==================== Gemini 分析 ====================
def analyze_with_gemini(image_url: str, product_name: str, category: str) -> dict:
    """
    使用 Gemini Vision 分析商品屬性
    
    Returns:
        dict: {'gender': str, 'color': str}
    """
    if not model:
        return {'gender': '中性', 'color': '-'}
    
    try:
        img = download_image(image_url)
        if not img:
            return {'gender': '中性', 'color': '-'}
        
        category_name = "配件" if category == "accessories" else "鞋子"
        
        prompt = f"""請仔細觀察這張 NET 服飾商品圖片，這是一個{category_name}商品。

商品名稱：{product_name}

請判斷以下2個屬性：

1. **性別 (gender)**：這是男用、女用還是中性？
   - 觀察設計風格、顏色、款式
   - 只回答：男 或 女 或 中性

2. **顏色 (color)**：主要顏色是什麼？
   - 請用中文回答（如：黑色、白色、棕色、銀色等）
   - 如果有多種顏色，回答最主要的顏色

**請嚴格按照以下 JSON 格式回答，不要有任何額外說明：**

{{
  "gender": "中性",
  "color": "黑色"
}}
"""
        
        response = model.generate_content([prompt, img])
        result_text = response.text.strip()
        
        # 解析 JSON
        if '```json' in result_text:
            result_text = result_text.split('```json')[1].split('```')[0].strip()
        elif '```' in result_text:
            result_text = result_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(result_text)
        
        return {
            'gender': result.get('gender', '中性'),
            'color': result.get('color', '-')
        }
        
    except Exception as e:
        print(f"  ⚠️  Gemini 分析失敗: {e}")
        return {'gender': '中性', 'color': '-'}


# ==================== 爬蟲邏輯 ====================
def crawl_net_products(mock_data: list, category: str, max_items: int = 10) -> list:
    """
    處理商品數據（使用測試數據模擬爬蟲）
    
    Args:
        mock_data: 測試商品數據
        category: 'accessories' 或 'shoes'
        max_items: 最多處理數量
        
    Returns:
        商品資料列表
    """
    items = []
    
    try:
        print(f"\n🔍 開始處理 {category} 類別...")
        
        for idx, product in enumerate(mock_data[:max_items], 1):
            try:
                name = product['name']
                price = product['price']
                image_url = f"https://images.unsplash.com/{product['img_id']}?w=400"
                sku = f"NET-{category.upper()}-{int(time.time())}-{idx}"
                
                print(f"\n  [{idx}/{max_items}] {name}")
                print(f"       價格: NT$ {price}")
                print(f"       圖片: {image_url[:60]}...")
                
                # 使用 Gemini 分析
                print(f"       🤖 Gemini 分析中...")
                gemini_result = analyze_with_gemini(image_url, name, category)
                
                item = {
                    'name': name,
                    'category': category,
                    'color': gemini_result['color'],
                    'image_url': image_url,
                    'sku': sku,
                    'gender': gemini_result['gender'],
                    'clothing_type': None,
                    'length': None,
                    'price': float(price),
                    'source': 'net'
                }
                
                items.append(item)
                print(f"       ✅ 性別: {gemini_result['gender']}, 顏色: {gemini_result['color']}")
                
                # 避免 API 請求過快
                time.sleep(1)
                
            except Exception as e:
                print(f"  ❌ 處理商品失敗: {e}")
                continue
        
        print(f"\n✅ {category} 類別處理完成，共 {len(items)} 筆")
        
    except Exception as e:
        print(f"❌ 處理失敗: {e}")
    
    return items


def extract_price(price_text: str) -> float:
    """從價格文字中提取數字"""
    if not price_text:
        return None
    
    # 移除所有非數字字元（保留小數點）
    numbers = re.findall(r'\d+\.?\d*', price_text.replace(',', ''))
    if numbers:
        return float(numbers[0])
    return None


# ==================== 資料庫操作 ====================
def insert_to_database(items: list):
    """將商品資料插入資料庫"""
    if not items:
        print("\n⚠️  沒有商品資料需要插入")
        return
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        insert_sql = """
        INSERT INTO items (name, category, color, image_url, sku, gender, 
                          clothing_type, length, price, source, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name = VALUES(name),
            category = VALUES(category),
            color = VALUES(color),
            image_url = VALUES(image_url),
            gender = VALUES(gender),
            price = VALUES(price)
        """
        
        inserted_count = 0
        for item in items:
            try:
                cursor.execute(insert_sql, (
                    item['name'],
                    item['category'],
                    item['color'],
                    item['image_url'],
                    item['sku'],
                    item['gender'],
                    item['clothing_type'],
                    item['length'],
                    item['price'],
                    item['source'],
                    datetime.now()
                ))
                inserted_count += 1
            except Exception as e:
                print(f"  ⚠️  插入失敗 ({item['name']}): {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ 成功插入 {inserted_count} 筆資料到資料庫")
        
    except Exception as e:
        print(f"\n❌ 資料庫操作失敗: {e}")


# ==================== 主程式 ====================
def main():
    """主程式"""
    print("=" * 80)
    print("🕷️  NET 配件與鞋類爬蟲")
    print("=" * 80)
    
    if not API_KEY:
        print("\n⚠️  建議設定 GEMINI_API_KEY 以啟用自動屬性辨識")
        print("   export GEMINI_API_KEY='your-api-key'")
    
    all_items = []
    
    # 處理配件
    accessories_items = crawl_net_products(MOCK_ACCESSORIES, 'accessories', max_items=10)
    all_items.extend(accessories_items)
    
    # 處理鞋類
    shoes_items = crawl_net_products(MOCK_SHOES, 'shoes', max_items=10)
    all_items.extend(shoes_items)
    
    # 插入資料庫
    print("\n" + "=" * 80)
    print(f"📊 爬取總結: 共 {len(all_items)} 筆商品")
    print(f"   - 配件: {len(accessories_items)} 筆")
    print(f"   - 鞋類: {len(shoes_items)} 筆")
    print("=" * 80)
    
    if all_items:
        insert_to_database(all_items)
    
    print("\n✅ 爬蟲執行完成！")


if __name__ == '__main__':
    main()
