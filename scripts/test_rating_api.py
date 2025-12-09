"""
API 測試腳本 - 評分權重推薦系統
使用 requests 庫進行測試

使用方式:
    python3 test_rating_api.py
"""

import requests
import json
from typing import Dict, Any

# 設定
BASE_URL = "http://localhost:5001"
USER_ID = 54
ITEM_SOURCE = "items"

# 顏色輸出 (ANSI)
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def print_header(text: str):
    """印出測試區塊標題"""
    print(f"\n{GREEN}{'=' * 50}")
    print(f"{text}")
    print(f"{'=' * 50}{NC}\n")


def print_test(name: str, method: str, endpoint: str):
    """印出測試名稱"""
    print(f"{YELLOW}測試: {name}{NC}")
    print(f"請求: {method} {endpoint}")


def print_response(response: requests.Response):
    """印出 API 回應"""
    print(f"狀態碼: {response.status_code}")
    try:
        data = response.json()
        print("回應:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
    except:
        print("回應 (非 JSON):")
        print(response.text)
    print(f"\n{'-' * 50}\n")


def test_api(name: str, method: str, endpoint: str, data: Dict = None) -> requests.Response:
    """執行 API 測試"""
    print_test(name, method, endpoint)
    
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if data:
                print(f"資料: {json.dumps(data, ensure_ascii=False)}")
            response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            raise ValueError(f"不支援的方法: {method}")
        
        print_response(response)
        return response
        
    except requests.exceptions.ConnectionError:
        print(f"{RED}❌ 連線失敗! 請確保 Flask 應用程式正在運行{NC}\n")
        return None
    except Exception as e:
        print(f"{RED}❌ 錯誤: {str(e)}{NC}\n")
        return None


def main():
    """主測試流程"""
    print(f"\n{BLUE}{'=' * 50}")
    print("評分權重推薦系統 API 測試")
    print(f"{'=' * 50}{NC}")
    
    # ===========================
    # 1. 測試提交評分
    # ===========================
    print_header("1. 測試提交評分")
    
    # 1.1 提交高分評分
    test_api(
        "提交高分評分 (5星)",
        "POST",
        "/recommendation/api/rating",
        {
            "item_id": 5092,
            "item_source": "items",
            "rating_value": 5,
            "review_text": "超級喜歡這件商品!"
        }
    )
    
    # 1.2 提交低分評分
    test_api(
        "提交低分評分 (2星)",
        "POST",
        "/recommendation/api/rating",
        {
            "item_id": 5102,
            "item_source": "items",
            "rating_value": 2,
            "review_text": "不太適合我"
        }
    )
    
    # 1.3 更新評分 (同一商品)
    test_api(
        "更新評分 (改為4星)",
        "POST",
        "/recommendation/api/rating",
        {
            "item_id": 5092,
            "item_source": "items",
            "rating_value": 4,
            "review_text": "重新評估後覺得是4星"
        }
    )
    
    # ===========================
    # 2. 測試推薦查詢
    # ===========================
    print_header("2. 測試推薦查詢")
    
    # 2.1 取得帶權重推薦
    test_api(
        "取得帶權重推薦 (前10件)",
        "GET",
        "/recommendation/api/recommendations?item_source=items&limit=10&exclude_rated=true"
    )
    
    # 2.2 取得推薦比較
    test_api(
        "推薦比較 (無權重 vs 有權重)",
        "GET",
        "/recommendation/api/recommendations/comparison?item_source=items&limit=5"
    )
    
    # 2.3 取得高評分商品
    test_api(
        "取得高評分商品 (前5件)",
        "GET",
        "/recommendation/api/top-rated?item_source=items&limit=5&min_rating_count=3"
    )
    
    # ===========================
    # 3. 測試用戶評分查詢
    # ===========================
    print_header("3. 測試用戶評分查詢")
    
    # 3.1 查詢用戶所有評分
    test_api(
        "查詢用戶所有評分",
        "GET",
        f"/recommendation/api/ratings/user/{USER_ID}?limit=10"
    )
    
    # 3.2 查詢用戶評分摘要
    test_api(
        "查詢用戶評分摘要",
        "GET",
        f"/recommendation/api/ratings/user/{USER_ID}/summary"
    )
    
    # ===========================
    # 4. 測試商品統計查詢
    # ===========================
    print_header("4. 測試商品統計查詢")
    
    # 4.1 查詢商品統計
    test_api(
        "查詢商品統計 (ID: 5092)",
        "GET",
        "/recommendation/api/item-stats/5092?item_source=items"
    )
    
    # 4.2 檢查是否已評分
    test_api(
        "檢查是否已評分 (ID: 5092)",
        "GET",
        "/recommendation/api/rating/check/5092?item_source=items"
    )
    
    # 4.3 檢查未評分商品
    test_api(
        "檢查未評分商品 (ID: 5120)",
        "GET",
        "/recommendation/api/rating/check/5120?item_source=items"
    )
    
    # ===========================
    # 5. 測試全站統計
    # ===========================
    print_header("5. 測試全站統計")
    
    test_api(
        "查詢全站評分統計",
        "GET",
        "/recommendation/api/statistics"
    )
    
    # ===========================
    # 6. 測試刪除評分
    # ===========================
    print_header("6. 測試刪除評分")
    
    # 6.1 刪除評分
    test_api(
        "刪除評分 (ID: 5102)",
        "DELETE",
        "/recommendation/api/rating/5102?item_source=items"
    )
    
    # 6.2 驗證刪除
    test_api(
        "驗證刪除結果",
        "GET",
        "/recommendation/api/rating/check/5102?item_source=items"
    )
    
    # 完成
    print(f"\n{GREEN}{'=' * 50}")
    print("測試完成!")
    print(f"{'=' * 50}{NC}\n")
    
    print("注意事項:")
    print("1. 確保 Flask 應用程式正在運行 (port 5001)")
    print("2. 確保 demo_user (ID: 54) 已建立")
    print("3. 確保測試商品 (ID: 5092-5121) 已存在")
    print("4. 測試前需先登入以取得 session cookie\n")


if __name__ == "__main__":
    main()
