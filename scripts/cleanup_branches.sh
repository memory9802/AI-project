#!/bin/bash
# ========================================
# AI-Project 分支整理腳本
# ========================================
# 
# ⚠️ 執行前請先閱讀: BRANCH_CLEANUP_PLAN.md
# 
# 此腳本會:
# 1. 備份舊 main
# 2. 用 openspec 覆蓋 main
# 3. 建立 develop 分支
# 4. 合併重要分支到 develop
# 5. 刪除不需要的分支
# 
# ========================================

set -e  # 遇到錯誤就停止

echo "🧹 AI-Project 分支整理腳本"
echo "========================================"
echo ""

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ========================================
# Phase 0: 確認
# ========================================

echo "⚠️  此腳本會進行重大變更:"
echo "  1. 用 openspec 覆蓋 main (舊 main 會備份到 main-old-backup)"
echo "  2. 建立新的 develop 分支"
echo "  3. 合併 Crawler&Detection 和 frontend"
echo "  4. 刪除 Jinja, jinja-test, integrate-crawler-db"
echo ""
echo "執行前請確認:"
echo "  - 所有組員已提交修改"
echo "  - 所有組員已被通知"
echo "  - 已閱讀 BRANCH_CLEANUP_PLAN.md"
echo ""

read -p "確定要繼續嗎? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "❌ 已取消"
    exit 0
fi

echo ""

# ========================================
# Phase 1: 備份與準備
# ========================================

echo "📋 Phase 1: 備份與準備"
echo "----------------------------------------"

# 更新所有分支資訊
echo "🔄 更新遠端分支資訊..."
git fetch --all

# 備份目前的工作
if ! git diff-index --quiet HEAD --; then
    echo "💾 發現未提交的修改,進行 stash..."
    git stash save "cleanup-script-auto-stash-$(date +%Y%m%d-%H%M%S)"
fi

# 顯示目前分支
echo ""
echo "📊 目前的分支:"
git branch -a
echo ""

sleep 2

# ========================================
# Phase 2: 建立新的 main (基於 openspec)
# ========================================

echo ""
echo "🔄 Phase 2: 建立新的 main (基於 openspec)"
echo "----------------------------------------"

# 切換到 main 並備份
echo "💾 備份舊 main 到 main-old-backup..."
git checkout main
git pull origin main
git branch -f main-old-backup main
git push origin main-old-backup

echo ""
echo -e "${YELLOW}⚠️  警告:即將用 openspec 覆蓋 main!${NC}"
echo "   舊 main 已備份到 main-old-backup 分支"
echo ""
read -p "確定繼續? (yes/no): " confirm_main
if [ "$confirm_main" != "yes" ]; then
    echo "❌ 已取消"
    exit 0
fi

# 用 openspec 覆蓋 main
echo "🔄 用 openspec 覆蓋 main..."
git checkout openspec
git pull origin openspec
git checkout main
git reset --hard openspec
echo "📤 推送新的 main..."
git push origin main --force

echo -e "${GREEN}✅ 新的 main 已建立 (基於 openspec)${NC}"
sleep 2

# ========================================
# Phase 3: 建立 develop 分支
# ========================================

echo ""
echo "🆕 Phase 3: 建立 develop 分支"
echo "----------------------------------------"

# 檢查 develop 是否已存在
if git show-ref --verify --quiet refs/heads/develop; then
    echo "⚠️  develop 分支已存在,刪除並重建..."
    git branch -D develop
fi

if git show-ref --verify --quiet refs/remotes/origin/develop; then
    echo "⚠️  遠端 develop 分支已存在,將會覆蓋..."
fi

# 從 main 建立 develop
echo "🔄 從 main 建立 develop..."
git checkout main
git checkout -b develop
git push origin develop --force

echo -e "${GREEN}✅ develop 分支已建立${NC}"
sleep 2

# ========================================
# Phase 4.1: 合併 Crawler&Detection
# ========================================

echo ""
echo "🔄 Phase 4.1: 合併 Crawler&Detection (爬蟲+資料庫)"
echo "----------------------------------------"

git checkout develop
git pull origin develop

echo "🔄 合併 Crawler&Detection..."
if git merge origin/Crawler&Detection -m "合併爬蟲和資料庫功能" --no-edit; then
    echo -e "${GREEN}✅ Crawler&Detection 合併成功${NC}"
else
    echo -e "${RED}⚠️  發生合併衝突!${NC}"
    echo ""
    echo "請手動解決衝突:"
    echo "  1. 編輯衝突檔案"
    echo "  2. git add <解決的檔案>"
    echo "  3. git commit -m '解決 Crawler&Detection 合併衝突'"
    echo "  4. 重新執行此腳本 (會跳過已完成的步驟)"
    echo ""
    echo "衝突檔案:"
    git status
    exit 1
fi

git push origin develop
sleep 2

# ========================================
# Phase 4.2: 合併 frontend
# ========================================

echo ""
echo "🔄 Phase 4.2: 合併 frontend (前端)"
echo "----------------------------------------"

git checkout develop
git pull origin develop

echo "🔄 合併 frontend..."
if git merge origin/frontend -m "合併前端網頁內容" --no-edit; then
    echo -e "${GREEN}✅ frontend 合併成功${NC}"
else
    echo -e "${RED}⚠️  發生合併衝突!${NC}"
    echo ""
    echo "請手動解決衝突:"
    echo "  1. 編輯衝突檔案"
    echo "  2. git add <解決的檔案>"
    echo "  3. git commit -m '解決 frontend 合併衝突'"
    echo "  4. 重新執行此腳本"
    echo ""
    echo "衝突檔案:"
    git status
    exit 1
fi

git push origin develop
sleep 2

# ========================================
# Phase 4.3: 提取 system 的 Windows 相容性
# ========================================

echo ""
echo "📋 Phase 4.3: 檢查 system 分支的 Windows 相容性修改"
echo "----------------------------------------"

echo "🔍 比較 openspec 和 system 的差異..."
git diff openspec system > /tmp/system-diff.txt

if [ -s /tmp/system-diff.txt ]; then
    echo "⚠️  發現差異,請手動檢查是否需要套用 Windows 相容性修改"
    echo "   差異檔案已儲存到: /tmp/system-diff.txt"
    echo ""
    read -p "是否要查看差異? (yes/no): " view_diff
    if [ "$view_diff" = "yes" ]; then
        less /tmp/system-diff.txt
    fi
    echo ""
    echo "如需套用 system 的修改,請手動:"
    echo "  1. 檢查 /tmp/system-diff.txt"
    echo "  2. 手動複製需要的修改到 develop"
    echo "  3. git add . && git commit -m 'Windows 相容性修改'"
else
    echo "✅ system 和 openspec 沒有差異"
fi

sleep 2

# ========================================
# Phase 5: 清理不需要的分支
# ========================================

echo ""
echo "🗑️  Phase 5: 清理不需要的分支"
echo "----------------------------------------"

echo "即將刪除以下分支:"
echo "  - Jinja (前後端串接測試,已過時)"
echo "  - jinja-test (測試用)"
echo "  - integrate-crawler-db (內容有誤)"
echo ""
read -p "確定刪除? (yes/no): " confirm_delete
if [ "$confirm_delete" = "yes" ]; then
    # 刪除遠端分支
    echo "🗑️  刪除遠端分支..."
    git push origin --delete Jinja 2>/dev/null || echo "  Jinja 不存在或已刪除"
    git push origin --delete jinja-test 2>/dev/null || echo "  jinja-test 不存在或已刪除"
    git push origin --delete integrate-crawler-db 2>/dev/null || echo "  integrate-crawler-db 不存在或已刪除"
    
    # 刪除本地分支
    echo "🗑️  刪除本地分支..."
    git branch -D Jinja 2>/dev/null || echo "  Jinja 不存在或已刪除"
    git branch -D jinja-test 2>/dev/null || echo "  jinja-test 不存在或已刪除"
    git branch -D integrate-crawler-db 2>/dev/null || echo "  integrate-crawler-db 不存在或已刪除"
    
    echo -e "${GREEN}✅ 不需要的分支已刪除${NC}"
else
    echo "⏭️  跳過刪除分支"
fi

sleep 2

# ========================================
# Phase 6: 清理遠端分支參照
# ========================================

echo ""
echo "🧹 Phase 6: 清理遠端分支參照"
echo "----------------------------------------"

git fetch --prune
echo -e "${GREEN}✅ 遠端分支參照已清理${NC}"

# ========================================
# 完成
# ========================================

echo ""
echo "========================================"
echo -e "${GREEN}🎉 分支整理完成!${NC}"
echo "========================================"
echo ""
echo "📊 最終分支架構:"
git branch -a
echo ""
echo "📋 下一步:"
echo "  1. 測試 develop 分支: git checkout develop"
echo "  2. 啟動 Docker: docker-compose up -d"
echo "  3. 測試資料庫: docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e 'SELECT COUNT(*) FROM items;'"
echo "  4. 測試 Flask: cd app && python3 app.py"
echo "  5. 通知組員新的分支架構"
echo ""
echo "📖 詳細說明: docs/GIT_WORKFLOW_GUIDE.md"
echo ""
echo "⚠️  如果需要恢復舊 main:"
echo "   git checkout main"
echo "   git reset --hard main-old-backup"
echo "   git push origin main --force"
echo ""
# Final
