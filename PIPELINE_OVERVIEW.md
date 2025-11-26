# UNIQLO 商品處理專案 - 檔案架構總覽

## 📂 關鍵程式檔案說明

### 🎯 核心流程檔案 (pipeline/)

| 檔案 | 功能 | 輸入 | 輸出 |
|------|------|------|------|
| **01_crawl_uniqlo.py** | UNIQLO爬蟲 + 基本欄位提取 | 網頁或現有CSV | `init/uniqlo_175.csv` |
| **02_detect_colors.py** | K-Means顏色辨識 + Pantone色號 | `uniqlo_175.csv` | `uniqlo_175_colored.csv` |
| **03_gemini_verify.py** | Gemini Vision API 全欄位驗證 | `uniqlo_175_colored.csv` | `gemini_verification_complete.csv` |
| **04_data_processing.py** | 資料合併、對比分析、統計報告 | 2個CSV | 3個分析CSV |
| **05_database_import.py** | 生成SQL腳本 + MySQL匯入 | `gemini_results_only.csv` | `outfit_db.sql` |

### 📋 完整執行流程

```bash
# 步驟1: 爬蟲
python pipeline/01_crawl_uniqlo.py

# 步驟2: 顏色辨識
python pipeline/02_detect_colors.py

# 步驟3: Gemini驗證 (需設定API Key)
export GEMINI_API_KEY='your-key'
python pipeline/03_gemini_verify.py

# 步驟4: 資料處理
python pipeline/04_data_processing.py

# 步驟5: 資料庫匯入
python pipeline/05_database_import.py
mysql -u root -p < init/outfit_db.sql
```

---

## 📁 專案結構

```
AI-project 2/
│
├── pipeline/                    # 🎯 核心流程檔案
│   ├── 01_crawl_uniqlo.py      # 爬蟲 + 基本欄位提取
│   ├── 02_detect_colors.py     # 顏色辨識 (K-Means + Pantone)
│   ├── 03_gemini_verify.py     # Gemini Vision API 驗證
│   ├── 04_data_processing.py   # 資料處理、合併、統計
│   ├── 05_database_import.py   # SQL生成 + 資料庫匯入
│   └── README.md               # 流程說明文件
│
├── init/                        # 📊 資料檔案目錄
│   ├── uniqlo_175.csv          # 原始爬取資料
│   ├── uniqlo_175_colored.csv  # + 顏色辨識
│   ├── gemini_verification_complete.csv  # + Gemini驗證
│   ├── gemini_results_only.csv           # 純Gemini結果
│   ├── gemini_comparison.csv             # 對比分析
│   ├── final_dataset.csv                 # 最終資料集
│   ├── outfit_db.sql                     # 資料庫腳本
│   └── generate_sql_import.py            # (舊版SQL生成，已整合)
│
├── docs/                        # 📚 文件目錄
│   ├── PROJECT_WORKFLOW.md     # 完整技術流程文件
│   ├── README.txt
│   ├── START_HERE.md
│   └── TEAM_COLLABORATION.md
│
├── other_projects/              # 🗂️ 其他專案範例
│   ├── 文件結構/petshop/       # Flask專案範例
│   └── style_rec_db/           # 風格推薦資料庫
│
├── dataset/                     # 🕷️ 其他爬蟲範例
│   ├── crawl_malefashion_items.py  # MaleFashion爬蟲
│   └── items_malefashion.csv
│
├── 歷史版本檔案/                 # 📦 開發過程檔案
│   ├── detectcolor.py          # 顏色辨識 v1
│   ├── detectcolor_v2.py ~ v10.py  # 各版本改進
│   ├── advanced_color_detection_*.py  # 進階版本
│   ├── gemini_full_verify.py   # Gemini驗證原型
│   ├── verify_fields.py        # 欄位驗證
│   └── 其他測試檔案...
│
└── app/                         # 🌐 Flask應用 (未來整合)
    ├── app.py
    ├── ai_agent.py
    ├── langchain_agent.py
    └── templates/
```

---

## 🎯 核心技術說明

### 1. 爬蟲與資料提取 (01_crawl_uniqlo.py)

**技術**:
- `requests` + `BeautifulSoup` 網頁解析
- 正則表達式從商品名稱提取屬性

**提取規則**:
```python
gender: '女' in name → '女', '男' in name → '男'
clothing_type: 'T恤/襯衫/外套' → '上衣', '褲/裙' → '下身'
length: '短袖/無袖' → '短', '長袖/長褲' → '長'
category: 組合 gender + type (如: 女裝T恤上衣)
```

---

### 2. 顏色辨識 (02_detect_colors.py)

**技術棧**:
- **K-Means 聚類**: 提取主色調
- **HSV 色相分析**: 優先判斷顏色類別
- **Pantone 色號系統**: 30+ 標準色號

**處理流程**:
```
下載圖片 → 去背(可選) → 過濾陰影 → K-Means → HSV分析 → Pantone匹配
```

**色號範例**:
- 黑色 (Pantone Black 6)
- 白色 (Pantone White)
- 深藍色 (Pantone 2767 C)
- 綠色 (Pantone 355 C)

---

### 3. Gemini Vision API 驗證 (03_gemini_verify.py)

**API**: Google Gemini 2.0 Flash  
**模型**: `gemini-2.0-flash-exp`

**驗證欄位**:
1. **gender**: 觀察剪裁、領口、模特兒
2. **category**: 細緻分類 (如: 女裝T恤上衣)
3. **clothing_type**: 上衣/下身
4. **length**: 長/短
5. **color**: 中文顏色名

**特色**:
- 結構化 JSON 輸出
- 自動解析與錯誤處理
- 每5筆自動存檔
- 支援中斷續傳

---

### 4. 資料處理 (04_data_processing.py)

**功能模組**:

1. **合併資料**: 原始 + Gemini驗證
2. **對比分析**: 逐欄位差異標記 (✓/❌)
3. **統計報告**: 準確率、差異範例
4. **最終資料集**: 混合策略（clothing_type用Gemini，color用Pantone）

**產出檔案**:
- `gemini_results_only.csv`: 純Gemini結果
- `gemini_comparison.csv`: 對比分析
- `final_dataset.csv`: 最終資料集

---

### 5. 資料庫匯入 (05_database_import.py)

**資料表結構**:

```sql
items (衣物表)
  - id, sku, name
  - gender, clothing_type, category, length
  - color, price, image_url

outfits (穿搭表)
outfit_items (關聯表)
tags (標籤表)
users (使用者表)
user_favorites (收藏表)
```

**欄位映射**:
- CSV `Gemini clothing_type` → SQL `category` (top/bottom)
- CSV `Gemini category` → SQL `clothing_type` (細分類)

---

## 📊 資料流轉圖

```
UNIQLO官網
    ↓ [01_crawl]
uniqlo_175.csv (175筆 × 8欄)
    ↓ [02_detect_colors]
uniqlo_175_colored.csv (+ color欄位)
    ↓ [03_gemini_verify]
gemini_verification_complete.csv (+ 5個Gemini欄位)
    ↓ [04_data_processing]
├── gemini_results_only.csv (231筆 × 9欄)
├── gemini_comparison.csv (對比分析)
└── final_dataset.csv (混合策略)
    ↓ [05_database_import]
outfit_db.sql (231條INSERT + 完整資料庫)
    ↓ [MySQL]
outfit_db 資料庫 (6個資料表)
```

---

## 🛠️ 環境需求

### Python 套件

```bash
# 核心
pip install pandas numpy pillow requests scikit-learn

# Gemini API
pip install google-generativeai

# 可選 (提升準確度)
pip install rembg opencv-python

# 資料庫 (可選)
pip install pymysql
```

### 環境變數

```bash
# Gemini API Key (必須)
export GEMINI_API_KEY='your-api-key'

# MySQL (可選)
export MYSQL_USER='root'
export MYSQL_PASSWORD='your-password'
```

---

## 🚀 快速開始

### 方法1: 完整流程

```bash
# 1. 設定環境
pip install -r requirements.txt
export GEMINI_API_KEY='your-key'

# 2. 執行完整流程
cd pipeline
python 01_crawl_uniqlo.py
python 02_detect_colors.py
python 03_gemini_verify.py
python 04_data_processing.py
python 05_database_import.py

# 3. 匯入資料庫
mysql -u root -p < ../init/outfit_db.sql
```

### 方法2: 使用現有資料

如果您已有 `init/` 目錄的CSV檔案：

```bash
# 直接從資料處理開始
cd pipeline
python 04_data_processing.py
python 05_database_import.py
```

---

## 📈 統計數據

### 資料集資訊

- **商品總數**: 231 筆
- **資料來源**: UNIQLO 台灣官網
- **時間**: 2024年
- **涵蓋類別**: 上衣、褲裝、裙裝

### Gemini 驗證準確率

| 欄位 | 原始vs Gemini差異 | 準確率 |
|------|------------------|--------|
| clothing_type | 1筆 | 99.5% |
| gender | 33筆 | 84.5% |
| length | 68筆 | 68.1% |
| category | 196筆 | 8.0% |
| color | 213筆 | 0.0% |

**分析**:
- ✅ **clothing_type** 幾乎完美
- ✅ **gender** 高準確率
- ⚠️ **category** 分類粒度差異（Gemini更細緻）
- ⚠️ **color** 格式差異（Gemini純中文 vs Pantone色號）

---

## 🔍 檔案整合說明

### 已整合檔案

| 原始檔案 | 整合後 | 說明 |
|---------|--------|------|
| `detectcolor.py` ~ `detectcolor_v10.py` | `02_detect_colors.py` | 顏色辨識演進版本 |
| `advanced_color_detection_*.py` | `02_detect_colors.py` | 進階算法整合 |
| `gemini_full_verify.py` | `03_gemini_verify.py` | Gemini驗證原型 |
| `restructure_csv.py` | `04_data_processing.py` | 資料重組功能 |
| `generate_sql_import.py` (init/) | `05_database_import.py` | SQL生成整合 |

### 保留的歷史檔案

專案根目錄的其他 `.py` 檔案為開發過程的歷史版本，保留作為參考：
- 演算法改進記錄
- 不同策略測試
- Bug修復歷程

---

## 📖 詳細文件

- **[pipeline/README.md](pipeline/README.md)** - 完整流程執行指南
- **[docs/PROJECT_WORKFLOW.md](docs/PROJECT_WORKFLOW.md)** - 技術細節文件
- **[GEMINI_QUICKSTART.md](GEMINI_QUICKSTART.md)** - Gemini API 使用教學

---

## ❓ 常見問題

### Q: 為什麼有這麼多顏色辨識版本？

A: 專案經歷多次算法改進：
- v1~v5: 基礎色彩聚類
- v6~v10: HSV色相優先 + 陰影過濾
- advanced: Pantone色號系統 + 背景去除

最終整合版 `02_detect_colors.py` 包含所有改進。

### Q: Gemini和原始資料哪個更準？

A: 根據欄位而定：
- **clothing_type**: Gemini準確率99.5%，建議使用Gemini
- **gender**: Gemini準確率84.5%，建議使用Gemini
- **color**: Pantone格式更規範，建議保留原始
- **category**: 看需求，Gemini更細緻但可能過於詳細

專案預設使用「混合策略」平衡準確性與格式。

### Q: 如何新增更多商品？

A: 修改 `01_crawl_uniqlo.py` 的爬取範圍，或合併多個CSV檔案後重新執行流程。

---

## 🎯 未來改進方向

1. **爬蟲優化**: Selenium支援動態網頁、增加錯誤重試
2. **顏色辨識**: 深度學習模型、多角度圖片融合
3. **Gemini整合**: 批次API、成本優化、Prompt工程
4. **資料庫**: 增加索引、全文搜尋、關聯推薦
5. **Web介面**: Flask應用整合、視覺化分析

---

**專案更新**: 2025-01-23  
**Python版本**: 3.8+  
**授權**: 學習研究用途
