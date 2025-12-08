#!/bin/bash
# =====================================
# Docker 完全清理並重建腳本
# 確保每次都使用最新配置
# =====================================

set -e  # 遇到錯誤立即停止

echo "🧹 開始 Docker 完全清理流程..."
echo "================================"

# 步驟 1: 停止並刪除所有容器
echo ""
echo "1️⃣  停止並刪除容器..."
docker-compose down -v || true
docker rm -f outfit-mysql outfit-flask outfit-phpmyadmin 2>/dev/null || true

# 步驟 2: 刪除所有相關 images
echo ""
echo "2️⃣  刪除舊的 Docker images..."
docker rmi stylerec-mysql stylerec-flask 2>/dev/null || true
docker rmi $(docker images -q stylerec-mysql) 2>/dev/null || true
docker rmi $(docker images -q stylerec-flask) 2>/dev/null || true

# 步驟 3: 刪除 volumes
echo ""
echo "3️⃣  刪除資料 volumes..."
docker volume rm stylerec_mysql_data 2>/dev/null || true

# 步驟 4: 清理 Docker build cache
echo ""
echo "4️⃣  清理 build cache..."
docker builder prune -f

# 步驟 5: 顯示清理結果
echo ""
echo "5️⃣  清理完成! 目前狀態:"
echo "   - Containers: $(docker ps -a | grep outfit | wc -l | tr -d ' ') 個"
echo "   - Images: $(docker images | grep stylerec | wc -l | tr -d ' ') 個"
echo "   - Volumes: $(docker volume ls | grep stylerec | wc -l | tr -d ' ') 個"

# 步驟 6: 重新建置
echo ""
echo "================================"
echo "🔨 開始重新建置..."
echo "================================"

# 先 build MySQL (使用 no-cache)
echo ""
echo "6️⃣  Building MySQL image..."
docker-compose build --no-cache mysql

# 再 build Flask
echo ""
echo "7️⃣  Building Flask image..."
docker-compose build --no-cache flask

# 步驟 7: 啟動服務
echo ""
echo "8️⃣  啟動所有服務..."
docker-compose up -d

# 步驟 8: 等待初始化
echo ""
echo "⏳ 等待資料庫初始化 (45 秒)..."
sleep 45

# 步驟 9: 驗證
echo ""
echo "================================"
echo "✅ 驗證結果"
echo "================================"

# 檢查容器狀態
echo ""
echo "📦 容器狀態:"
docker-compose ps

# 檢查 MySQL logs
echo ""
echo "📝 MySQL 初始化日誌 (最後 10 行):"
docker logs outfit-mysql --tail 10

# 檢查資料庫結構
echo ""
echo "🗄️  Items 表結構:"
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db \
  -e "DESCRIBE items;" 2>/dev/null | grep -v "Warning"

# 檢查資料量
echo ""
echo "📊 資料統計:"
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db \
  -e "SELECT 'items' as table_name, COUNT(*) as count FROM items 
      UNION ALL 
      SELECT 'users', COUNT(*) FROM users;" 2>/dev/null | grep -v "Warning"

echo ""
echo "================================"
echo "✅ 重建完成!"
echo "================================"
echo ""
echo "🌐 服務連結:"
echo "   - Flask 應用: http://localhost:5001"
echo "   - phpMyAdmin: http://localhost:8080"
echo "   - MySQL: localhost:3306"
echo ""
echo "💡 提示:"
echo "   - 如果需要查看完整日誌: docker logs outfit-mysql"
echo "   - 如果需要進入容器: docker exec -it outfit-mysql bash"
echo ""
