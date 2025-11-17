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

# 保持 __main__ 區塊不變，用於獨立測試
if __name__ == '__main__':
    llm_prompt, json_data = get_clothing_summary_for_llm(TEST_USER_ID, "正式", "15度")
    if "沒有任何衣物數據" not in llm_prompt:
        print("\n--- 成功從資料庫抓取數據並轉換為 LLM Prompt ---")
        print(llm_prompt)
    else:
        print("\n--- 資料抓取失敗，請檢查資料庫連線 ---")