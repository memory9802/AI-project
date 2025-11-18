# ~/Desktop/stylerec/data_processor.py

import pandas as pd
import json
import mysql.connector # 使用這個套件來連接 MySQL
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE # 匯入連線參數

# --- 全域變數 (用於方便 LLM 推薦) ---
TEST_USER_ID = 99 # 專門用於測試的用戶 ID

def get_db_connection():
    """建立並回傳一個 MySQL 資料庫連線物件。"""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE,
            # 確保使用舊式密碼認證，以避免 Public Key Retrieval 錯誤
            auth_plugin='mysql_native_password' 
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def fetch_clothing_data_from_db(user_id):
    """
    從 MySQL 資料庫中讀取特定用戶的衣物數據，並回傳 Pandas DataFrame。
    """
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame() # 連線失敗則回傳空 DataFrame

    try:
        # 課綱：MySQL 查詢資料
        query = f"""
            SELECT clothing_id, category, color, material, tags
            FROM Clothing
            WHERE user_id = {user_id};
        """
        # 使用 Pandas 內建功能直接從 SQL 查詢結果建立 DataFrame
        # 課綱：Pandas 介紹 / 載入資料
        df = pd.read_sql(query, conn)
        return df
        
    except Exception as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()
    finally:
        # 確保連線被關閉，釋放資源
        conn.close()

def get_clothing_summary_for_llm(user_id, current_occasion="", current_temp_range=""):
    """將衣物數據轉換為 LLM 易於理解的純文字摘要。"""
    df = fetch_clothing_data_from_db(user_id)
    
    if df.empty:
        return "使用者衣櫃目前沒有任何衣物數據。", ""
        
    # --- 數據轉換 (與先前邏輯相同，使用 Pandas 組合字串) ---
    df['summary_text'] = (
        "ID " + df['clothing_id'].astype(str) + ": " + 
        "類別: " + df['category'] + ", " + 
        "顏色: " + df['color'] + ", " + 
        "材質: " + df['material'] + ", " + 
        "標籤: " + df['tags']
    )
    
    text_summary = "\n- ".join(df['summary_text'].tolist())
    
    llm_prompt_summary = (
        f"目前場合: {current_occasion}, 溫度: {current_temp_range}\n"
        "使用者衣櫃現有衣物清單 (請從中選擇搭配):\n"
        f"- {text_summary}"
    )
    
    # 這裡我們也回傳一個 JSON 格式，方便 LLM 進行結構化輸出
    clothing_list_json = df[['clothing_id', 'category', 'color', 'material', 'tags']].to_json(orient='records', force_ascii=False)
    
    return llm_prompt_summary, clothing_list_json


def fetch_images_by_ids(item_ids):
    """
    根據 LLM 推薦的 item_id 清單，從 Item 表格中獲取圖片路徑及必要細節。
    """
    if not item_ids:
        return []

    conn = get_db_connection()
    if conn is None:
        return []

    try:
        # 使用 IN 語句一次查詢所有推薦的 ID
        # 將 item_ids 列表轉換為 SQL 語句可用的逗號分隔字串
        ids_str = ','.join(map(str, item_ids)) 
        
        query = f"""
            SELECT item_id, name, category, color, image_path, is_user_owned, price
            FROM Item
            WHERE item_id IN ({ids_str});
        """
        
        # 課綱：Pandas 介紹 / 載入資料 [cite: 7]
        df = pd.read_sql(query, conn)
        
        # 將 DataFrame 轉換為 Python 列表，方便 Flask 回傳 JSON
        # 課綱：資料清洗與轉換 [cite: 7]
        result_list = df.to_dict(orient='records')
        
        return result_list
        
    except Exception as e:
        print(f"Error fetching images by IDs: {e}")
        return []
    finally:
        conn.close()


# --- 測試區塊 (可選，但建議執行) ---
if __name__ == '__main__':
    # 測試 LLM 推薦的正式穿搭 ID: 2002, 2008, 2010
    test_ids = [2002, 2008, 2010] 
    
    outfit_details = fetch_images_by_ids(test_ids)
    
    print("\n--- 根據 ID 查詢到的穿搭細節 ---")
    if outfit_details:
        for item in outfit_details:
            print(f"ID: {item['item_id']}, 名稱: {item['name']}, 圖片路徑: {item['image_path']}")
    else:
        print("查詢失敗或未找到資料。")