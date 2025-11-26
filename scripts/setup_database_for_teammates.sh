#!/bin/bash
# 組員快速建立資料庫環境

echo "=================================="
echo "🚀 快速建立 outfit_db 資料庫"
echo "=================================="
echo ""

# 檢查 Docker 是否運行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未運行,請先啟動 Docker Desktop"
    exit 1
fi

# 1. 啟動 MySQL 容器
echo "1️⃣ 啟動 MySQL 容器..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo "❌ 容器啟動失敗"
    exit 1
fi

echo "⏳ 等待 MySQL 啟動完成..."
sleep 15

# 2. 檢查檔案是否存在
if [ ! -f "init/outfit_db_with_data.sql" ]; then
    echo "❌ 找不到 init/outfit_db_with_data.sql"
    echo "📝 請確認:"
    echo "   1. 已執行 git pull"
    echo "   2. 在專案根目錄執行此腳本"
    exit 1
fi

# 3. 匯入資料庫
echo ""
echo "2️⃣ 匯入資料庫 (包含 50 個用戶 + 49,707 筆商品)..."
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

if [ $? -ne 0 ]; then
    echo "❌ 資料庫匯入失敗"
    exit 1
fi

# 4. 驗證資料
echo ""
echo "3️⃣ 驗證資料..."
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT '📊 資料庫統計' as info;
SELECT '' as blank;
SELECT 'users 表' as table_name, COUNT(*) as count FROM users
UNION ALL
SELECT 'items 表' as table_name, COUNT(*) as count FROM items;
"

echo ""
echo "=================================="
echo "✅ 資料庫建立完成!"
echo "=================================="
echo ""
echo "🔑 測試帳號:"
echo "   用戶名: admin"
echo "   密碼: admin123"
echo ""
echo "📊 DBeaver 連接資訊:"
echo "   Host: localhost"
echo "   Port: 3306"
echo "   Database: outfit_db"
echo "   Username: root"
echo "   Password: rootpassword"
echo ""
echo "📚 更多資訊請查看: docs/DATABASE_SHARING_GUIDE.md"
