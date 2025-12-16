// ==========================================
// 評分推薦系統 API 測試 (瀏覽器版)
// 在瀏覽器開發者工具的 Console 中執行
// ==========================================

const BASE_URL = 'http://localhost:5001';

// 測試結果收集
const results = {
    total: 0,
    passed: 0,
    failed: 0,
    tests: []
};

// 輔助函數: 發送請求
async function apiTest(name, method, endpoint, body = null) {
    results.total++;
    console.log(`\n🧪 測試 ${results.total}: ${name}`);
    console.log(`   ${method} ${endpoint}`);
    
    try {
        const options = {
            method: method,
            credentials: 'include', // 使用瀏覽器的 cookie
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
            console.log('   請求內容:', body);
        }
        
        const response = await fetch(BASE_URL + endpoint, options);
        const data = await response.json();
        
        if (data.success) {
            results.passed++;
            console.log('   ✅ 成功!');
            console.log('   回應:', data);
            results.tests.push({ name, status: '✅ 成功', data });
        } else {
            results.failed++;
            console.log('   ❌ 失敗:', data.error || data.message);
            results.tests.push({ name, status: '❌ 失敗', error: data.error || data.message });
        }
        
        return data;
    } catch (error) {
        results.failed++;
        console.log('   ❌ 錯誤:', error.message);
        results.tests.push({ name, status: '❌ 錯誤', error: error.message });
        return null;
    }
}

// 執行測試
async function runTests() {
    console.log('==========================================');
    console.log('🚀 開始測試評分推薦系統 API');
    console.log('==========================================');
    
    // 測試 1: 取得推薦 (帶權重)
    const recommendations = await apiTest(
        '取得推薦商品 (帶權重)',
        'GET',
        '/recommendation/api/recommendations?item_source=items&limit=5&exclude_rated=false'
    );
    
    // 測試 2: 全站統計
    await apiTest(
        '查詢全站統計',
        'GET',
        '/recommendation/api/statistics'
    );
    
    // 測試 3: 提交評分 (使用推薦列表中的第一件商品)
    let itemId = 1; // 預設
    if (recommendations && recommendations.data && recommendations.data.length > 0) {
        itemId = recommendations.data[0].id;
        console.log(`\n   使用商品 ID: ${itemId}`);
    }
    
    const ratingResult = await apiTest(
        '提交評分',
        'POST',
        '/recommendation/api/rating',
        {
            item_id: itemId,
            item_source: 'items',
            rating_value: 5,
            review_text: '測試評分 - 很棒的商品!'
        }
    );
    
    // 測試 4: 更新評分 (相同商品)
    await apiTest(
        '更新評分 (相同商品)',
        'POST',
        '/recommendation/api/rating',
        {
            item_id: itemId,
            item_source: 'items',
            rating_value: 4,
            review_text: '更新評分測試'
        }
    );
    
    // 測試 5: 檢查是否已評分
    await apiTest(
        '檢查是否已評分',
        'GET',
        `/recommendation/api/rating/check/${itemId}?item_source=items`
    );
    
    // 測試 6: 查詢商品統計
    await apiTest(
        '查詢商品統計',
        'GET',
        `/recommendation/api/item-stats/${itemId}?item_source=items`
    );
    
    // 測試 7: 查詢用戶評分記錄 (需要先取得 user_id)
    // 從瀏覽器的某個 API 取得當前用戶 ID
    try {
        const userResponse = await fetch(BASE_URL + '/recommendation/api/statistics', {
            credentials: 'include'
        });
        const userData = await userResponse.json();
        
        // 假設可以從某處取得 user_id,這裡用一個佔位符
        console.log('\n⚠️  需要用戶 ID 才能測試用戶評分查詢');
        console.log('   請在瀏覽器 Console 手動執行:');
        console.log('   fetch("http://localhost:5001/recommendation/api/ratings/user/YOUR_USER_ID?limit=5", {credentials: "include"}).then(r=>r.json()).then(console.log)');
    } catch (e) {
        console.log('   無法自動取得用戶 ID');
    }
    
    // 測試 8: 推薦比較 (無權重 vs 有權重)
    await apiTest(
        '推薦比較 (無權重 vs 有權重)',
        'GET',
        '/recommendation/api/recommendations/comparison?item_source=items&limit=3'
    );
    
    // 測試 9: 高評分商品
    await apiTest(
        '高評分商品列表',
        'GET',
        '/recommendation/api/top-rated?item_source=items&limit=5&min_rating_count=1'
    );
    
    // 測試 10: 刪除評分
    await apiTest(
        '刪除評分',
        'DELETE',
        `/recommendation/api/rating/${itemId}?item_source=items`
    );
    
    // 顯示總結
    console.log('\n==========================================');
    console.log('📊 測試總結');
    console.log('==========================================');
    console.log(`總測試數: ${results.total}`);
    console.log(`✅ 成功: ${results.passed}`);
    console.log(`❌ 失敗: ${results.failed}`);
    console.log(`成功率: ${((results.passed / results.total) * 100).toFixed(1)}%`);
    console.log('\n詳細結果:');
    console.table(results.tests);
    
    return results;
}

// 執行測試
console.log('複製以下命令到瀏覽器 Console 執行:');
console.log('runTests()');

// 如果要立即執行,取消下面這行的註解:
// runTests();
