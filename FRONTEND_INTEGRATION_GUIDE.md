# 評分權重推薦系統 - 前端整合指南

**版本**: v1.0  
**日期**: 2024-12-12  
**後端負責人**: [你的名字]  
**狀態**: ✅ 後端開發完成,待前端整合

---

## 📋 目錄

1. [功能概述](#功能概述)
2. [API 端點說明](#api-端點說明)
3. [前端整合步驟](#前端整合步驟)
4. [程式碼範例](#程式碼範例)
5. [UI/UX 建議](#uiux-建議)
6. [測試方法](#測試方法)
7. [常見問題](#常見問題)

---

## 🎯 功能概述

### 核心功能

本次更新實現了**帶權重的商品推薦系統**,根據以下兩個維度計算推薦分數:

1. **評分權重** (rating_weight)
   - 基於商品平均評分 (1-5 星)
   - 分數範圍: 0.5 - 1.5

2. **人氣權重** (popularity_weight)
   - 基於評分次數
   - 分數範圍: 1.0 - 1.3

3. **綜合分數** (final_score)
   - final_score = rating_weight × popularity_weight
   - 用於排序推薦結果

### 權重計算公式

```javascript
// 評分權重
function getRatingWeight(avgRating) {
    if (avgRating >= 4.5) return 1.5;
    if (avgRating >= 3.5) return 1.25;
    if (avgRating >= 2.5) return 1.0;
    if (avgRating >= 1.5) return 0.75;
    return 0.5;
}

// 人氣權重
function getPopularityWeight(ratingCount) {
    if (ratingCount >= 20) return 1.3;
    if (ratingCount >= 10) return 1.2;
    if (ratingCount >= 5) return 1.1;
    return 1.0;
}

// 綜合分數
const finalScore = getRatingWeight(avgRating) * getPopularityWeight(ratingCount);
```

---

## 🌐 API 端點說明

### 基礎資訊

- **基礎 URL**: `http://localhost:5001/recommendation/api`
- **認證方式**: Session Cookie (需先登入)
- **回應格式**: JSON

---

### 1. 取得帶權重推薦

**端點**: `GET /recommendations`

**Query Parameters**:
```javascript
{
    item_source: 'items',        // 'items' 或 'user_wardrobe'
    limit: 20,                   // 返回數量,預設 20
    exclude_rated: true,         // 是否排除已評分商品,預設 true
    min_rating: 4.0,            // (可選) 最低平均評分過濾
    category: '上衣'            // (可選) 商品類別過濾
}
```

**請求範例**:
```javascript
fetch('/recommendation/api/recommendations?item_source=items&limit=10&exclude_rated=true', {
    method: 'GET',
    credentials: 'include'  // 重要: 帶上 session cookie
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('推薦商品:', data.data);
        console.log('商品數量:', data.count);
    }
});
```

**回應格式**:
```json
{
    "success": true,
    "data": [
        {
            "id": 5092,
            "name": "短版T恤(短袖)",
            "category": "top",
            "color": "白色",
            "price": "390.00",
            "image_url": "https://...",
            
            // 權重相關欄位 ⭐
            "avg_rating": "5.00",          // 平均評分
            "rating_count": 12,            // 評分次數
            "rating_weight": "1.5",        // 評分權重
            "popularity_weight": "1.2",    // 人氣權重
            "final_score": "1.80",         // 綜合分數
            
            // 其他商品欄位...
        },
        // ...更多商品
    ],
    "count": 10
}
```

---

### 2. 提交評分

**端點**: `POST /rating`

**Request Body**:
```json
{
    "item_id": 5092,
    "item_source": "items",
    "rating_value": 5,                    // 必要: 1-5 星
    "review_text": "很棒的商品!"           // 可選: 評論文字
}
```

**請求範例**:
```javascript
fetch('/recommendation/api/rating', {
    method: 'POST',
    credentials: 'include',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        item_id: 5092,
        item_source: 'items',
        rating_value: 5,
        review_text: '超級喜歡!'
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        alert('評分提交成功!');
    } else {
        alert('錯誤: ' + data.error);
    }
});
```

**回應格式**:
```json
{
    "success": true,
    "message": "評分提交成功"
}
```

---

### 3. 查詢用戶評分記錄

**端點**: `GET /ratings/user/<user_id>`

**請求範例**:
```javascript
// 假設當前用戶 ID 是 58
fetch('/recommendation/api/ratings/user/58?limit=10', {
    method: 'GET',
    credentials: 'include'
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('評分記錄:', data.data);
    }
});
```

**回應格式**:
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "user_id": 58,
            "item_id": 5092,
            "item_source": "items",
            "rating_value": 5,
            "review_text": "很棒!",
            "created_at": "2024-12-12T10:30:00",
            "updated_at": "2024-12-12T10:30:00"
        }
    ],
    "count": 1
}
```

---

### 4. 檢查是否已評分

**端點**: `GET /rating/check/<item_id>`

**請求範例**:
```javascript
fetch('/recommendation/api/rating/check/5092?item_source=items', {
    method: 'GET',
    credentials: 'include'
})
.then(response => response.json())
.then(data => {
    if (data.rated) {
        console.log('已評分:', data.data.rating_value);
    } else {
        console.log('尚未評分');
    }
});
```

---

### 5. 查詢全站統計

**端點**: `GET /statistics`

**請求範例**:
```javascript
fetch('/recommendation/api/statistics', {
    method: 'GET',
    credentials: 'include'
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('總評分數:', data.data.total_ratings);
        console.log('平均評分:', data.data.avg_rating);
    }
});
```

---

## 🔧 前端整合步驟

### 步驟 1: 修改推薦頁面 (recommendation.html)

在商品列表中顯示權重資訊:

```html
<!-- 商品卡片範例 -->
<div class="product-card" data-product-id="5092">
    <img src="商品圖片URL" alt="商品名稱">
    <h3>短版T恤(短袖)</h3>
    <p class="price">$390</p>
    
    <!-- 新增: 評分顯示 -->
    <div class="rating-info">
        <span class="stars">⭐⭐⭐⭐⭐</span>
        <span class="avg-rating">5.0</span>
        <span class="rating-count">(12 評分)</span>
    </div>
    
    <!-- 新增: 權重資訊 (可選,可隱藏在開發者模式) -->
    <div class="weight-info" style="display: none;">
        <small>評分權重: 1.5</small>
        <small>人氣權重: 1.2</small>
        <small>綜合分數: 1.80</small>
    </div>
    
    <!-- 新增: 評分按鈕 -->
    <button class="rate-btn" onclick="openRatingModal(5092)">
        評分此商品
    </button>
</div>
```

---

### 步驟 2: 建立評分彈窗組件

```html
<!-- 評分彈窗 Modal -->
<div id="ratingModal" class="modal" style="display: none;">
    <div class="modal-content">
        <span class="close" onclick="closeRatingModal()">&times;</span>
        <h2>評分商品</h2>
        
        <div id="productInfo">
            <!-- 商品資訊 -->
        </div>
        
        <!-- 星級評分選擇器 -->
        <div class="star-rating">
            <span class="star" data-value="1">☆</span>
            <span class="star" data-value="2">☆</span>
            <span class="star" data-value="3">☆</span>
            <span class="star" data-value="4">☆</span>
            <span class="star" data-value="5">☆</span>
        </div>
        <p class="rating-text">請選擇評分</p>
        
        <!-- 評論文字 (可選) -->
        <textarea id="reviewText" placeholder="分享你的想法... (可選)" 
                  rows="4" maxlength="500"></textarea>
        
        <!-- 提交按鈕 -->
        <button onclick="submitRating()">提交評分</button>
    </div>
</div>
```

---

### 步驟 3: JavaScript 核心功能實現

```javascript
// =====================================
// 1. 取得推薦商品列表 (帶權重)
// =====================================
async function loadRecommendations() {
    try {
        const response = await fetch('/recommendation/api/recommendations?item_source=items&limit=20&exclude_rated=true', {
            method: 'GET',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayProducts(data.data);
        } else {
            console.error('載入推薦失敗:', data.error);
        }
    } catch (error) {
        console.error('請求錯誤:', error);
    }
}

// =====================================
// 2. 顯示商品列表
// =====================================
function displayProducts(products) {
    const container = document.getElementById('productContainer');
    container.innerHTML = '';
    
    products.forEach(product => {
        const card = createProductCard(product);
        container.appendChild(card);
    });
}

function createProductCard(product) {
    const card = document.createElement('div');
    card.className = 'product-card';
    card.dataset.productId = product.id;
    
    // 計算星星顯示
    const fullStars = Math.floor(product.avg_rating);
    const halfStar = (product.avg_rating % 1) >= 0.5;
    const starsHTML = '⭐'.repeat(fullStars) + (halfStar ? '½' : '');
    
    card.innerHTML = `
        <img src="${product.image_url}" alt="${product.name}">
        <h3>${product.name}</h3>
        <p class="price">$${product.price}</p>
        <div class="rating-info">
            <span class="stars">${starsHTML}</span>
            <span class="avg-rating">${parseFloat(product.avg_rating).toFixed(1)}</span>
            <span class="rating-count">(${product.rating_count} 評分)</span>
        </div>
        <button class="rate-btn" onclick="openRatingModal(${product.id}, '${product.name}')">
            評分此商品
        </button>
    `;
    
    return card;
}

// =====================================
// 3. 評分功能
// =====================================
let currentProductId = null;
let selectedRating = 0;

function openRatingModal(productId, productName) {
    currentProductId = productId;
    selectedRating = 0;
    
    // 顯示商品資訊
    document.getElementById('productInfo').innerHTML = `
        <p>商品: ${productName}</p>
    `;
    
    // 重置星星
    document.querySelectorAll('.star').forEach(star => {
        star.textContent = '☆';
        star.classList.remove('selected');
    });
    
    // 清空評論
    document.getElementById('reviewText').value = '';
    
    // 顯示彈窗
    document.getElementById('ratingModal').style.display = 'block';
}

function closeRatingModal() {
    document.getElementById('ratingModal').style.display = 'none';
}

// 星星點擊事件
document.addEventListener('DOMContentLoaded', function() {
    const stars = document.querySelectorAll('.star');
    
    stars.forEach(star => {
        star.addEventListener('click', function() {
            selectedRating = parseInt(this.dataset.value);
            
            // 更新星星顯示
            stars.forEach((s, index) => {
                if (index < selectedRating) {
                    s.textContent = '★';
                    s.classList.add('selected');
                } else {
                    s.textContent = '☆';
                    s.classList.remove('selected');
                }
            });
            
            // 更新文字提示
            const texts = ['', '很差', '普通', '不錯', '很好', '超棒!'];
            document.querySelector('.rating-text').textContent = texts[selectedRating];
        });
        
        // Hover 效果
        star.addEventListener('mouseenter', function() {
            const value = parseInt(this.dataset.value);
            stars.forEach((s, index) => {
                if (index < value) {
                    s.textContent = '★';
                } else if (index >= selectedRating) {
                    s.textContent = '☆';
                }
            });
        });
    });
    
    // 滑鼠離開時恢復選中狀態
    document.querySelector('.star-rating').addEventListener('mouseleave', function() {
        stars.forEach((s, index) => {
            if (index < selectedRating) {
                s.textContent = '★';
            } else {
                s.textContent = '☆';
            }
        });
    });
});

// 提交評分
async function submitRating() {
    if (selectedRating === 0) {
        alert('請選擇評分!');
        return;
    }
    
    const reviewText = document.getElementById('reviewText').value.trim();
    
    try {
        const response = await fetch('/recommendation/api/rating', {
            method: 'POST',
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                item_id: currentProductId,
                item_source: 'items',
                rating_value: selectedRating,
                review_text: reviewText || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('評分提交成功!');
            closeRatingModal();
            
            // 重新載入推薦列表 (顯示更新後的評分)
            loadRecommendations();
        } else {
            alert('錯誤: ' + data.error);
        }
    } catch (error) {
        console.error('提交評分失敗:', error);
        alert('提交失敗,請稍後再試');
    }
}

// =====================================
// 4. 頁面載入時執行
// =====================================
window.addEventListener('load', function() {
    loadRecommendations();
});
```

---

### 步驟 4: CSS 樣式

```css
/* 商品卡片 */
.product-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 15px;
    margin: 10px;
    width: 200px;
    display: inline-block;
    vertical-align: top;
}

.product-card img {
    width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: 4px;
}

/* 評分資訊 */
.rating-info {
    margin: 10px 0;
    font-size: 14px;
}

.stars {
    color: #FFD700;
    font-size: 16px;
}

.avg-rating {
    font-weight: bold;
    margin-left: 5px;
}

.rating-count {
    color: #666;
    font-size: 12px;
}

/* 評分按鈕 */
.rate-btn {
    background-color: #4CAF50;
    color: white;
    border: none;
    padding: 10px 15px;
    border-radius: 4px;
    cursor: pointer;
    width: 100%;
    margin-top: 10px;
}

.rate-btn:hover {
    background-color: #45a049;
}

/* 評分彈窗 */
.modal {
    position: fixed;
    z-index: 1000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
}

.modal-content {
    background-color: white;
    margin: 10% auto;
    padding: 30px;
    border-radius: 8px;
    width: 400px;
    max-width: 90%;
}

.close {
    float: right;
    font-size: 28px;
    font-weight: bold;
    cursor: pointer;
}

.close:hover {
    color: #f00;
}

/* 星級評分選擇器 */
.star-rating {
    text-align: center;
    margin: 20px 0;
}

.star {
    font-size: 40px;
    cursor: pointer;
    color: #ddd;
    transition: color 0.2s;
}

.star:hover,
.star.selected {
    color: #FFD700;
}

.rating-text {
    text-align: center;
    font-size: 18px;
    color: #666;
    margin: 10px 0;
}

/* 評論文字框 */
#reviewText {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    resize: vertical;
}

/* 提交按鈕 */
.modal-content button {
    background-color: #2196F3;
    color: white;
    border: none;
    padding: 12px 30px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
    width: 100%;
    margin-top: 15px;
}

.modal-content button:hover {
    background-color: #0b7dda;
}
```

---

## 🎨 UI/UX 建議

### 1. 評分顯示

**建議位置**: 商品卡片底部,價格下方

```
┌─────────────────┐
│   商品圖片      │
├─────────────────┤
│ 商品名稱        │
│ $390           │
│ ⭐⭐⭐⭐⭐ 5.0  │  ← 評分顯示
│ (12 評分)      │
│ [評分此商品]    │  ← 評分按鈕
└─────────────────┘
```

### 2. 評分按鈕狀態

- **未評分**: 顯示 "評分此商品" (綠色按鈕)
- **已評分**: 顯示 "已評分 ★★★★★" (灰色按鈕)
- **Hover**: 按鈕顏色加深

### 3. 評分彈窗設計

```
┌────────────────────────────┐
│  評分商品              [✕] │
├────────────────────────────┤
│  商品: 短版T恤(短袖)       │
│                            │
│      ☆ ☆ ☆ ☆ ☆           │  ← 可點擊的星星
│     請選擇評分             │
│                            │
│  ┌──────────────────────┐ │
│  │ 分享你的想法... (可選)│ │
│  │                      │ │
│  └──────────────────────┘ │
│                            │
│      [提交評分]            │
└────────────────────────────┘
```

### 4. 互動反饋

- ✅ 提交成功: 顯示成功提示,關閉彈窗,刷新列表
- ❌ 提交失敗: 顯示錯誤訊息,保留彈窗內容
- ⏳ 載入中: 顯示 Loading 動畫

---

## 🧪 測試方法

### 1. 功能測試清單

- [ ] 頁面載入後自動顯示推薦商品
- [ ] 商品卡片正確顯示評分資訊
- [ ] 點擊 "評分此商品" 彈出評分彈窗
- [ ] 星星選擇功能正常 (點擊和 Hover)
- [ ] 評分提交成功後顯示提示
- [ ] 提交後推薦列表更新
- [ ] 已評分商品顯示不同狀態

### 2. API 測試工具

在瀏覽器開發者工具 Console 中測試:

```javascript
// 測試 1: 取得推薦
fetch('/recommendation/api/recommendations?limit=5', {
    credentials: 'include'
}).then(r => r.json()).then(console.log);

// 測試 2: 提交評分
fetch('/recommendation/api/rating', {
    method: 'POST',
    credentials: 'include',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        item_id: 5092,
        item_source: 'items',
        rating_value: 5,
        review_text: '測試評分'
    })
}).then(r => r.json()).then(console.log);

// 測試 3: 查詢評分記錄
fetch('/recommendation/api/ratings/user/58?limit=5', {
    credentials: 'include'
}).then(r => r.json()).then(console.log);
```

### 3. 測試端點 (不需登入)

為方便測試,後端提供了不需登入的測試端點:

```javascript
// 測試推薦功能 (不需登入)
fetch('/recommendation/api/test/recommendations?limit=5')
    .then(r => r.json())
    .then(console.log);

// 測試統計功能 (不需登入)
fetch('/recommendation/api/test/statistics')
    .then(r => r.json())
    .then(console.log);
```

---

## ❓ 常見問題

### Q1: API 返回 401 Unauthorized

**原因**: 用戶未登入或 session 過期

**解決方案**:
```javascript
// 確保請求帶上 credentials
fetch(url, {
    credentials: 'include'  // 重要!
})
```

### Q2: 提交評分後推薦列表沒有更新

**原因**: 需要手動刷新推薦列表

**解決方案**:
```javascript
async function submitRating() {
    // ... 提交評分 ...
    
    if (data.success) {
        alert('評分提交成功!');
        closeRatingModal();
        
        // 重新載入推薦列表
        await loadRecommendations();  // ← 加上這行
    }
}
```

### Q3: 權重欄位為 null 或 0

**原因**: 商品尚未有評分

**解決方案**: 這是正常情況,前端需要處理:
```javascript
const avgRating = product.avg_rating || 0;
const ratingCount = product.rating_count || 0;

if (ratingCount === 0) {
    // 顯示 "尚無評分"
} else {
    // 顯示評分資訊
}
```

### Q4: 如何顯示半顆星?

**方案 1**: 使用 Unicode
```javascript
function getStarsHTML(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = (rating % 1) >= 0.5;
    
    return '★'.repeat(fullStars) + 
           (halfStar ? '½' : '') + 
           '☆'.repeat(5 - fullStars - (halfStar ? 1 : 0));
}
```

**方案 2**: 使用 CSS
```css
.stars {
    position: relative;
    display: inline-block;
}

.stars::before {
    content: '☆☆☆☆☆';
}

.stars::after {
    content: '★★★★★';
    position: absolute;
    left: 0;
    width: 80%;  /* 根據評分動態設置 */
    overflow: hidden;
}
```

---

## 📞 技術支援

### 後端相關問題

- **負責人**: [你的名字]
- **聯絡方式**: [你的 Email 或 Slack]

### API 文檔

- **完整文檔**: `docs/RATING_SYSTEM_COMPLETE_GUIDE.md`
- **測試腳本**: `test_weight_system.py`

### 測試環境

- **API URL**: `http://localhost:5001/recommendation/api`
- **測試帳號**: 
  - Email: `aaa`
  - Password: `aaaaaa`

---

## 📝 更新日誌

### v1.0 (2024-12-12)
- ✅ 初始版本
- ✅ 實現帶權重推薦 API
- ✅ 實現評分提交 API
- ✅ 實現評分查詢 API
- ✅ 提供測試端點

---

## 🎯 檢查清單

前端開發完成前,請確認:

- [ ] 已閱讀完整文檔
- [ ] 測試過所有 API 端點
- [ ] 實現了評分顯示功能
- [ ] 實現了評分提交功能
- [ ] 處理了錯誤情況
- [ ] 測試了使用者流程
- [ ] 確認 UI/UX 符合設計規範
- [ ] 與後端測試聯調成功

---

**準備好了嗎? 開始整合吧! 🚀**

如有任何問題,請隨時聯繫後端團隊。
