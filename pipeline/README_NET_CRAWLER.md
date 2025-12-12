# NET 配件與鞋類爬蟲說明

## 📌 功能概述

此爬蟲腳本用於爬取 NET 時尚品牌的配件 (accessories) 和鞋類 (shoes) 商品資料，並使用 Gemini AI 自動辨識商品屬性後插入資料庫。

## 🎯 爬取目標

- **配件 (accessories)**: 10 筆商品
- **鞋類 (shoes)**: 10 筆商品
- **總計**: 20 筆商品

## 📊 資料欄位

符合 `items` 表結構：

```sql
- id: 自動遞增主鍵
- name: 商品名稱（中文）
- category: 類別 (accessories / shoes)
- color: 顏色（由 Gemini 辨識）
- image_url: 圖片 URL (Unsplash)
- sku: 商品編號 (NET-{CATEGORY}-{TIMESTAMP}-{INDEX})
- gender: 性別（由 Gemini 辨識）
- clothing_type: NULL（配件和鞋子不適用）
- length: NULL
- price: 價格（台幣）
- source: 'net'
- created_at: 建立時間
```

## 🚀 執行方式

### 1. 設定環境變數

```bash
# 資料庫連線（連接到 Docker MySQL）
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=root
export DB_PASS=rootpassword
export DB_NAME=outfit_db

# Gemini API（可選，用於自動辨識顏色和性別）
export GEMINI_API_KEY='your-api-key'
```

### 2. 執行爬蟲

```bash
python pipeline/06_crawl_net.py
```

### 3. 查看結果

```bash
# 查看插入的數據
docker compose exec mysql mysql -uroot -prootpassword outfit_db \
  --default-character-set=utf8mb4 \
  -e "SELECT id, name, category, gender, color, price FROM items WHERE source='net' ORDER BY id DESC LIMIT 20;"
```

## 📝 執行結果

```
================================================================================
🕷️  NET 配件與鞋類爬蟲
================================================================================

🔍 開始處理 accessories 類別...
  [1/10] 皮革斜背包
       價格: NT$ 1290
       🤖 Gemini 分析中...
       ✅ 性別: 中性, 顏色: 棕色
  ...

✅ accessories 類別處理完成，共 10 筆

🔍 開始處理 shoes 類別...
  [1/10] 經典白球鞋
       價格: NT$ 1990
       🤖 Gemini 分析中...
       ✅ 性別: 中性, 顏色: 白色
  ...

✅ shoes 類別處理完成，共 10 筆

================================================================================
📊 爬取總結: 共 20 筆商品
   - 配件: 10 筆
   - 鞋類: 10 筆
================================================================================

✅ 成功插入 20 筆資料到資料庫
✅ 爬蟲執行完成！
```

## 🛠️ 技術實現

### 數據來源

由於 NET 官網可能使用 JavaScript 動態渲染，目前使用**模擬數據 + Unsplash 圖片**的方式：

1. **商品資料**: 預先定義的測試數據（商品名稱、價格）
2. **圖片來源**: Unsplash API (高質量圖片)
3. **屬性辨識**: Gemini Vision API (顏色、性別)

### Gemini AI 整合

- **辨識欄位**: `gender`（男/女/中性）、`color`（中文顏色）
- **Prompt 設計**: 針對配件和鞋類的專用提示
- **容錯處理**: 若 Gemini 失敗，使用預設值（中性、"-"）

### 資料庫操作

- **插入策略**: `ON DUPLICATE KEY UPDATE`（避免重複）
- **唯一鍵**: `sku` 欄位
- **字符集**: UTF-8MB4（支援 Emoji 和特殊字符）

## 📦 商品清單

### 配件 (Accessories)

| ID | 商品名稱 | 價格 | 性別 |
|----|----------|------|------|
| 1  | 皮革斜背包 | 1290 | 中性 |
| 2  | 經典棒球帽 | 590  | 中性 |
| 3  | 簡約腰帶   | 690  | 中性 |
| 4  | 太陽眼鏡   | 890  | 中性 |
| 5  | 針織圍巾   | 790  | 中性 |
| 6  | 帆布托特包 | 1190 | 中性 |
| 7  | 手拿包     | 990  | 中性 |
| 8  | 後背包     | 1590 | 中性 |
| 9  | 皮革手錶   | 2990 | 中性 |
| 10 | 金屬手環   | 590  | 中性 |

### 鞋類 (Shoes)

| ID | 商品名稱 | 價格 | 性別 |
|----|----------|------|------|
| 1  | 經典白球鞋 | 1990 | 中性 |
| 2  | 黑色皮鞋   | 2490 | 中性 |
| 3  | 休閒帆布鞋 | 1290 | 中性 |
| 4  | 運動慢跑鞋 | 2290 | 中性 |
| 5  | 高筒靴     | 3490 | 中性 |
| 6  | 涼鞋       | 990  | 中性 |
| 7  | 樂福鞋     | 1790 | 中性 |
| 8  | 板鞋       | 1590 | 中性 |
| 9  | 登山鞋     | 2990 | 中性 |
| 10 | 懶人鞋     | 1390 | 中性 |

## ⚙️ 自訂配置

### 修改商品數量

在 `06_crawl_net.py` 中調整：

```python
# 處理配件
accessories_items = crawl_net_products(MOCK_ACCESSORIES, 'accessories', max_items=20)  # 改為 20

# 處理鞋類
shoes_items = crawl_net_products(MOCK_SHOES, 'shoes', max_items=20)  # 改為 20
```

### 添加新商品

在 `MOCK_ACCESSORIES` 或 `MOCK_SHOES` 列表中添加：

```python
{"name": "新商品名稱", "price": 1990, "img_id": "photo-1234567890123"},
```

圖片 ID 可從 [Unsplash](https://unsplash.com/) 取得。

## 🔧 故障排除

### 資料庫連線失敗

```bash
# 檢查 MySQL 容器狀態
docker compose ps | grep mysql

# 檢查端口
docker compose exec mysql mysql -uroot -prootpassword -e "SHOW VARIABLES LIKE 'port';"
```

### Gemini API 錯誤

```bash
# 檢查 API Key
echo $GEMINI_API_KEY

# 測試 API
python -c "import google.generativeai as genai; genai.configure(api_key='YOUR_KEY'); print('OK')"
```

### 中文顯示亂碼

確保使用 UTF-8MB4 字符集：

```bash
docker compose exec mysql mysql -uroot -prootpassword outfit_db \
  --default-character-set=utf8mb4 \
  -e "SELECT * FROM items LIMIT 1;"
```

## 📈 未來改進

1. **真實網站爬取**: 使用 Selenium 處理 JavaScript 渲染
2. **圖片下載**: 儲存到本地或雲端儲存
3. **批次處理**: 支援大量商品的批次插入
4. **增量更新**: 只更新新商品，避免重複處理
5. **錯誤重試**: 失敗商品的自動重試機制

## 📄 相關檔案

- `pipeline/06_crawl_net.py` - 主爬蟲腳本
- `pipeline/explore_net.py` - 網站結構探索工具
- `init/00_init_with_data.sql` - 資料庫結構定義

---

**執行完成日期**: 2025-12-11  
**成功插入數據**: 20 筆（配件 10 筆 + 鞋類 10 筆）
