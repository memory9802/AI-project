"""
UNIQLO 商品爬蟲
從 UNIQLO 台灣官網爬取商品資料並儲存為 CSV

輸出: init/uniqlo_raw.csv
欄位: sku, name, price, image_url
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from typing import List, Dict

# 配置
BASE_URL = "https://www.uniqlo.com/tw/zh_TW"
HEADERS = {
<<<<<<< HEAD
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.uniqlo.com/",
}


def crawl_category_page(
    category_url: str, max_items: int = 100, seen_skus: set = None
) -> List[Dict]:
    """
    爬取指定類別頁面的商品列表

    Args:
        category_url: 類別頁面URL
        max_items: 最多爬取數量
        seen_skus: 已爬取的 SKU 集合（用於去重）

    Returns:
        商品資料列表
    """
    if seen_skus is None:
        seen_skus = set()

    items = []
    skipped_count = 0

    try:
        response = requests.get(category_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # 根據 UNIQLO 網站結構找商品區塊
        product_blocks = soup.select(".product-tile")  # 需根據實際網站調整

        for block in product_blocks[:max_items]:
            try:
                # 提取 SKU
                sku = block.get("data-product-id", "")

                # 🔥 新增: SKU 去重檢查
                if sku in seen_skus:
                    skipped_count += 1
                    print(f"    跳過重複 SKU: {sku}")
                    continue

                # 提取商品名稱
                name_tag = block.select_one(".product-name")
                name = name_tag.text.strip() if name_tag else ""

                # 提取價格
                price_tag = block.select_one(".price")
                price = price_tag.text.strip() if price_tag else ""

                # 提取圖片URL
                img_tag = block.select_one("img")
                image_url = img_tag.get("src", "") if img_tag else ""

                if sku and name:
                    items.append(
                        {
                            "sku": sku,
                            "name": name,
                            "price": price,
                            "image_url": image_url,
                        }
                    )
                    seen_skus.add(sku)  # 🔥 記錄已爬取的 SKU

            except Exception as e:
                print(f"處理商品區塊失敗: {e}")
                continue

        if skipped_count > 0:
            print(f"    (跳過 {skipped_count} 筆重複商品)")
        print(f"成功爬取 {len(items)} 筆商品")

    except Exception as e:
        print(f"爬取頁面失敗: {e}")

=======
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://www.uniqlo.com/',
}

def crawl_category_page(category_url: str, max_items: int = 100) -> List[Dict]:
    """
    爬取指定類別頁面的商品列表
    
    Args:
        category_url: 類別頁面URL
        max_items: 最多爬取數量
        
    Returns:
        商品資料列表
    """
    items = []
    
    try:
        response = requests.get(category_url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 根據 UNIQLO 網站結構找商品區塊
        product_blocks = soup.select('.product-tile')  # 需根據實際網站調整
        
        for block in product_blocks[:max_items]:
            try:
                # 提取 SKU
                sku = block.get('data-product-id', '')
                
                # 提取商品名稱
                name_tag = block.select_one('.product-name')
                name = name_tag.text.strip() if name_tag else ''
                
                # 提取價格
                price_tag = block.select_one('.price')
                price = price_tag.text.strip() if price_tag else ''
                
                # 提取圖片URL
                img_tag = block.select_one('img')
                image_url = img_tag.get('src', '') if img_tag else ''
                
                if sku and name:
                    items.append({
                        'sku': sku,
                        'name': name,
                        'price': price,
                        'image_url': image_url
                    })
                    
            except Exception as e:
                print(f"處理商品區塊失敗: {e}")
                continue
                
        print(f"成功爬取 {len(items)} 筆商品")
        
    except Exception as e:
        print(f"爬取頁面失敗: {e}")
        
>>>>>>> memory9802/blueprints-success
    return items


def extract_basic_info(items: List[Dict]) -> pd.DataFrame:
    """
    從商品名稱中提取基本資訊 (gender, category, clothing_type, length)
<<<<<<< HEAD

    Args:
        items: 原始商品資料列表

=======
    
    Args:
        items: 原始商品資料列表
        
>>>>>>> memory9802/blueprints-success
    Returns:
        包含額外欄位的 DataFrame
    """
    df = pd.DataFrame(items)
<<<<<<< HEAD

    # 性別判斷規則
    def extract_gender(name: str) -> str:
        if "女" in name or "女性" in name or "女士" in name or "女裝" in name:
            return "女"
        elif (
            "男" in name or "男性" in name or "男士" in name or "男裝" in name
        ):
            return "男"
        return "-"

    # 服裝類型判斷
    def extract_clothing_type(name: str) -> str:
        if any(
            x in name for x in ["T恤", "上衣", "襯衫", "外套", "衛衣", "POLO"]
        ):
            return "上衣"
        elif any(x in name for x in ["褲", "裙", "短褲", "九分褲"]):
            return "下身"
        return "-"

    # 類別細分
    def extract_category(name: str) -> str:
        if "T恤" in name:
            return "女裝T恤上衣" if "女" in name else "男裝T恤上衣"
        elif "襯衫" in name:
            return "女裝襯衫" if "女" in name else "男裝襯衫"
        elif "牛仔褲" in name:
            return "女裝牛仔褲" if "女" in name else "男裝牛仔褲"
        elif "長褲" in name:
            return "女裝長褲" if "女" in name else "男裝長褲"
        return "-"

    # 長度判斷
    def extract_length(name: str) -> str:
        if any(x in name for x in ["短袖", "短版", "無袖", "五分袖", "短褲"]):
            return "短"
        elif any(x in name for x in ["長袖", "長版", "長褲", "九分"]):
            return "長"
        return "-"

    # 應用提取函數
    df["gender"] = df["name"].apply(extract_gender)
    df["category"] = df["name"].apply(extract_category)
    df["clothing_type"] = df["name"].apply(extract_clothing_type)
    df["length"] = df["name"].apply(extract_length)

=======
    
    # 性別判斷規則
    def extract_gender(name: str) -> str:
        if '女' in name or '女性' in name or '女士' in name or '女裝' in name:
            return '女'
        elif '男' in name or '男性' in name or '男士' in name or '男裝' in name:
            return '男'
        return '-'
    
    # 服裝類型判斷
    def extract_clothing_type(name: str) -> str:
        if any(x in name for x in ['T恤', '上衣', '襯衫', '外套', '衛衣', 'POLO']):
            return '上衣'
        elif any(x in name for x in ['褲', '裙', '短褲', '九分褲']):
            return '下身'
        return '-'
    
    # 類別細分
    def extract_category(name: str) -> str:
        if 'T恤' in name:
            return '女裝T恤上衣' if '女' in name else '男裝T恤上衣'
        elif '襯衫' in name:
            return '女裝襯衫' if '女' in name else '男裝襯衫'
        elif '牛仔褲' in name:
            return '女裝牛仔褲' if '女' in name else '男裝牛仔褲'
        elif '長褲' in name:
            return '女裝長褲' if '女' in name else '男裝長褲'
        return '-'
    
    # 長度判斷
    def extract_length(name: str) -> str:
        if any(x in name for x in ['短袖', '短版', '無袖', '五分袖', '短褲']):
            return '短'
        elif any(x in name for x in ['長袖', '長版', '長褲', '九分']):
            return '長'
        return '-'
    
    # 應用提取函數
    df['gender'] = df['name'].apply(extract_gender)
    df['category'] = df['name'].apply(extract_category)
    df['clothing_type'] = df['name'].apply(extract_clothing_type)
    df['length'] = df['name'].apply(extract_length)
    
>>>>>>> memory9802/blueprints-success
    return df


def main():
    """主程式流程"""
    print("=" * 80)
    print("🕷️  UNIQLO 商品爬蟲")
    print("=" * 80)
<<<<<<< HEAD

=======
    
>>>>>>> memory9802/blueprints-success
    # 方法1: 如果你有現成的商品列表CSV (例如從網站API獲取)
    # 可以直接讀取並處理
    try:
        # 假設已有初步爬取的資料
<<<<<<< HEAD
        raw_file = "init/uniqlo_175.csv"
        print(f"\n讀取現有資料: {raw_file}")
        df = pd.read_csv(raw_file)
        print(f"✅ 讀取 {len(df)} 筆商品")

    except FileNotFoundError:
        # 方法2: 實際爬取 (需根據網站結構調整)
        print("\n開始爬取 UNIQLO 商品...")

=======
        raw_file = 'init/uniqlo_175.csv'
        print(f"\n讀取現有資料: {raw_file}")
        df = pd.read_csv(raw_file)
        print(f"✅ 讀取 {len(df)} 筆商品")
        
    except FileNotFoundError:
        # 方法2: 實際爬取 (需根據網站結構調整)
        print("\n開始爬取 UNIQLO 商品...")
        
>>>>>>> memory9802/blueprints-success
        # 定義要爬取的類別URL
        categories = [
            f"{BASE_URL}/women/tops",
            f"{BASE_URL}/women/bottoms",
            f"{BASE_URL}/men/tops",
            f"{BASE_URL}/men/bottoms",
        ]
<<<<<<< HEAD

        all_items = []
        seen_skus = set()  # 🔥 新增: 用於全域去重

        for cat_url in categories:
            print(f"\n爬取類別: {cat_url}")
            items = crawl_category_page(
                cat_url, max_items=50, seen_skus=seen_skus
            )
            all_items.extend(items)
            time.sleep(2)  # 避免請求過快

        print(f"\n✅ 總共爬取 {len(all_items)} 筆獨立商品")
        print(f"   (去重後，原始可能更多)")

        df = pd.DataFrame(all_items)
        print(f"\n✅ DataFrame 包含 {len(df)} 筆商品")

        # 儲存原始資料
        output_file = "init/uniqlo_raw.csv"
        df.to_csv(output_file, index=False, encoding="utf-8")
        print(f"✅ 原始資料已儲存: {output_file}")

=======
        
        all_items = []
        for cat_url in categories:
            print(f"\n爬取類別: {cat_url}")
            items = crawl_category_page(cat_url, max_items=50)
            all_items.extend(items)
            time.sleep(2)  # 避免請求過快
            
        df = pd.DataFrame(all_items)
        print(f"\n✅ 總共爬取 {len(df)} 筆商品")
        
        # 儲存原始資料
        output_file = 'init/uniqlo_raw.csv'
        df.to_csv(output_file, index=False, encoding='utf-8')
        print(f"✅ 原始資料已儲存: {output_file}")
    
>>>>>>> memory9802/blueprints-success
    # 提取基本資訊
    print("\n" + "=" * 80)
    print("📝 從商品名稱提取基本資訊")
    print("=" * 80)
<<<<<<< HEAD

    df_processed = extract_basic_info(df.to_dict("records"))

    # 顯示統計
    print(f"\n性別分布:")
    print(df_processed["gender"].value_counts())
    print(f"\n服裝類型分布:")
    print(df_processed["clothing_type"].value_counts())

    # 儲存處理後的資料
    output_file = "init/uniqlo_175.csv"
    df_processed.to_csv(output_file, index=False, encoding="utf-8")
    print(f"\n✅ 處理後資料已儲存: {output_file}")
    print(f"   欄位: {', '.join(df_processed.columns)}")


if __name__ == "__main__":
=======
    
    df_processed = extract_basic_info(df.to_dict('records'))
    
    # 顯示統計
    print(f"\n性別分布:")
    print(df_processed['gender'].value_counts())
    print(f"\n服裝類型分布:")
    print(df_processed['clothing_type'].value_counts())
    
    # 儲存處理後的資料
    output_file = 'init/uniqlo_175.csv'
    df_processed.to_csv(output_file, index=False, encoding='utf-8')
    print(f"\n✅ 處理後資料已儲存: {output_file}")
    print(f"   欄位: {', '.join(df_processed.columns)}")
    

if __name__ == '__main__':
>>>>>>> memory9802/blueprints-success
    main()
