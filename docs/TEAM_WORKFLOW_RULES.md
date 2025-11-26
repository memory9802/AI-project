# 🤝 團隊協作規範

## 🎯 資料庫同步黃金規則

### ⚠️ 規則 1: 統一檔名 (最重要!)

**所有人必須遵守:**
```
✅ 正確: init/outfit_db_with_data.sql
❌ 錯誤: init/outfit_db_<任何其他名字>.sql
```

**為什麼?**
- Git 自動追蹤版本,不需要檔名加日期
- 避免團隊成員搞混「哪個是最新版本」
- 腳本和文檔都指向同一個檔案

---

### 📋 規則 2: 標準工作流程

#### 情境 A: 你修改了資料庫

```bash
# 1. 匯出 (自動覆蓋 outfit_db_with_data.sql)
./scripts/export_database.sh

# 2. 查看變更
git diff init/outfit_db_with_data.sql | head -50

# 3. 提交
git add init/outfit_db_with_data.sql
git commit -m "更新資料庫:新增 500 個 UNIQLO 秋冬商品"

# 4. 推送
git push origin Crawler&Detection

# 5. 通知組員 (Line/Discord/Slack)
```

**通知訊息範本:**
```
📢 資料庫已更新

更新內容: 新增 500 個 UNIQLO 秋冬商品
更新時間: 2025-11-26 14:30

請執行以下指令同步:
1. git pull
2. docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

查詢驗證: SELECT COUNT(*) FROM items WHERE source='uniqlo';
預期結果: 721 (原 221 + 新增 500)
```

---

#### 情境 B: 收到「資料庫已更新」通知

```bash
# 1. 下載最新版本
git pull origin Crawler&Detection

# 2. 檢查檔案是否更新
ls -lh init/outfit_db_with_data.sql

# 3. 重新匯入資料庫
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 4. 驗證 (使用通知訊息中的查詢)
docker exec outfit-mysql mysql -uroot -prootpassword outfit_db -e "
SELECT COUNT(*) FROM items WHERE source='uniqlo';
"

# 5. 回報完成 (讓通知者放心)
# 「✅ 已同步,資料正確」
```

---

#### 情境 C: 兩人同時修改資料庫 (衝突處理)

**症狀:**
```bash
git push
# error: failed to push some refs
# hint: Updates were rejected because the remote contains work
```

**發生原因:**
- 張三匯出並 push 了 `outfit_db_with_data.sql`
- 李四也修改資料庫並嘗試 push
- Git 檢測到衝突

**解決方法 (重要!):**

```bash
# 1. 先下載最新版本
git pull origin Crawler&Detection
# 會顯示: CONFLICT (content): Merge conflict in init/outfit_db_with_data.sql

# 2. ⚠️ 不要手動編輯 SQL 檔案!
#    正確做法:決定「誰的資料比較完整」

# 選項 A: 使用遠端版本 (張三的)
git checkout --theirs init/outfit_db_with_data.sql
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

# 選項 B: 使用本地版本 (李四的)
git checkout --ours init/outfit_db_with_data.sql

# 3. 如果需要合併兩人的資料
#    a. 使用遠端版本
git checkout --theirs init/outfit_db_with_data.sql
docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

#    b. 再執行李四的 Python 腳本 (重新爬蟲/匯入)
python3 pipeline/01_crawl_uniqlo.py
python3 pipeline/05_database_import.py

#    c. 重新匯出
./scripts/export_database.sh

# 4. 提交解決後的版本
git add init/outfit_db_with_data.sql
git commit -m "解決衝突:合併張三和李四的資料"
git push

# 5. 通知組員
# 「⚠️ 剛解決資料庫衝突,已合併所有資料,請重新同步」
```

---

### 🕷️ 規則 3: 爬蟲組特殊規範

**口訣:** 爬完 → 匯出 → Commit → Push → 通知

**每次爬完資料必須執行:**
```bash
./scripts/crawler_upload_helper.sh
```

**為什麼?**
- ❌ 只在本地資料庫 = 其他人看不到
- ❌ 只上傳 CSV = 別人還要手動匯入,容易出錯
- ✅ 匯出 SQL = 一鍵同步,不會出錯

**檢查清單:**
- [ ] 資料已匯入到資料庫 (SELECT COUNT(*) 確認)
- [ ] 執行 `./scripts/crawler_upload_helper.sh`
- [ ] Git push 成功
- [ ] 已通知組員 (Line/Discord)
- [ ] 提供驗證查詢 (SELECT COUNT(*) WHERE source='xxx')

---

## 🚫 常見錯誤與預防

### ❌ 錯誤 1: 自創檔名

```bash
# ❌ 錯誤做法
docker exec outfit-mysql mysqldump ... > init/outfit_db_20251126.sql
git add init/outfit_db_20251126.sql

# ❌ 結果
init/
├─ outfit_db_with_data.sql      ← 組員看到這個
├─ outfit_db_20251126.sql       ← 你以為這個是最新
├─ outfit_db_20251127.sql       ← 隔天又建一個
└─ outfit_db_final_really.sql   ← 最後完全混亂 😱
```

**預防:**
- ✅ 永遠使用 `./scripts/export_database.sh` (自動使用正確檔名)
- ✅ 不要手動執行 mysqldump

---

### ❌ 錯誤 2: 忘記 Push

```bash
# 你的電腦
git commit -m "更新資料庫"
# ❌ 忘記 git push

# 組員的電腦
git pull
# 看不到你的更新!
```

**預防:**
- ✅ 使用 `./scripts/crawler_upload_helper.sh` (會提醒你 push)
- ✅ Commit 後立刻 push
- ✅ Push 後通知組員

---

### ❌ 錯誤 3: 只匯入 CSV,沒有匯出 SQL

```bash
# 爬蟲組員
python3 pipeline/01_crawl_uniqlo.py
python3 pipeline/05_database_import.py
# ✅ 資料在你的資料庫

# ❌ 忘記匯出並 push

# 其他組員
SELECT * FROM items WHERE source='uniqlo';
# 結果:看不到新資料!
```

**預防:**
- ✅ 記住口訣:「爬完 → 匯出 → Commit → Push → 通知」
- ✅ 每次爬完執行 `./scripts/crawler_upload_helper.sh`

---

### ❌ 錯誤 4: 直接編輯 outfit_db_with_data.sql

```bash
# ❌ 錯誤:用編輯器修改 SQL 檔案
vim init/outfit_db_with_data.sql
# 手動加入 INSERT INTO ...

# 問題:
# 1. 容易出錯 (語法錯誤、編碼問題)
# 2. 你的本地資料庫和檔案不一致
# 3. 其他人匯入可能失敗
```

**正確做法:**
```bash
# ✅ 正確:修改資料庫,然後匯出
# 1. 在資料庫中修改
INSERT INTO items (name, category, ...) VALUES (...);

# 2. 匯出
./scripts/export_database.sh

# 3. 提交
git add init/outfit_db_with_data.sql
git commit -m "新增測試資料"
git push
```

---

## ✅ 最佳實踐

### 1. 清楚的 Commit Message

```bash
# ✅ 好的 commit message
git commit -m "更新資料庫:新增 500 個 UNIQLO 秋冬商品"
git commit -m "修正資料庫:移除重複的 SKU"
git commit -m "更新用戶資料:新增 10 個測試帳號"

# ❌ 不好的 commit message
git commit -m "更新"
git commit -m "fix"
git commit -m "asdf"
```

**格式建議:**
```
更新資料庫:<簡短說明>

詳細內容:
- 新增 500 個 UNIQLO 商品
- 來源:2024 秋冬目錄
- 類別:上衣 200、褲子 150、外套 150

驗證查詢:
SELECT COUNT(*) FROM items WHERE source='uniqlo' AND category='上衣';
預期結果:200
```

---

### 2. 通知組員的完整訊息

```
📢 資料庫更新通知

👤 更新人: 張三
📅 時間: 2025-11-26 14:30
🔢 Commit: a1b2c3d

📝 更新內容:
- 新增 UNIQLO 秋冬商品 500 筆
- 更新商品圖片 URL
- 修正重複 SKU 問題

🔄 同步指令:
1. git pull origin Crawler&Detection
2. docker exec -i outfit-mysql mysql -uroot -prootpassword outfit_db < init/outfit_db_with_data.sql

✅ 驗證:
SELECT source, COUNT(*) FROM items GROUP BY source;
預期看到:
- uniqlo: 721 (原 221 + 新 500)
- styles_dataset: 44,407
- fashion_small: 4,999
- malefashion: 80

❓ 問題請回覆此訊息
```

---

### 3. 定期備份 (可選)

如果擔心資料遺失,可以定期備份:

```bash
# 每週備份一次 (可選)
mkdir -p backups
cp init/outfit_db_with_data.sql backups/outfit_db_$(date +%Y%m%d).sql.bak

# 備份檔案不要 commit 到 Git
echo "backups/" >> .gitignore
```

---

## 📊 檔案管理策略

### 目前策略 (推薦)

```
init/
├─ outfit_db_with_data.sql  ← 唯一的資料庫備份 (所有人共用)
├─ outfit_db.sql            ← 結構定義參考 (不含資料)
└─ README.md                ← 使用說明
```

**優點:**
- ✅ 簡單明確,不會混亂
- ✅ Git 自動追蹤版本歷史
- ✅ 所有人都知道「最新版本」是哪個

**Git 歷史查詢:**
```bash
# 查看更新歷史
git log --oneline init/outfit_db_with_data.sql

# 查看特定版本
git show <commit-hash>:init/outfit_db_with_data.sql | head -100

# 恢復舊版本 (如果需要)
git checkout <commit-hash> init/outfit_db_with_data.sql
```

---

### 不推薦的策略 ❌

```
❌ 策略 1: 每次都建新檔案
init/
├─ outfit_db_20251126_v1.sql
├─ outfit_db_20251126_v2.sql
├─ outfit_db_20251127_john.sql
├─ outfit_db_20251127_mary.sql
└─ outfit_db_final_really_final_v3.sql  😱

問題:
- 不知道哪個是最新
- 檔案爆炸
- Git 倉庫變巨大
```

```
❌ 策略 2: 每人一個資料夾
init/
├─ john/
│   └─ outfit_db.sql
├─ mary/
│   └─ outfit_db.sql
└─ peter/
    └─ outfit_db.sql

問題:
- 無法合併資料
- 不知道用誰的版本
- 協作困難
```

---

## 🎓 總結

### 記住這些規則

1. ✅ **統一檔名**: `init/outfit_db_with_data.sql`
2. ✅ **使用腳本**: `./scripts/export_database.sh`
3. ✅ **完整流程**: 匯出 → Commit → Push → 通知
4. ✅ **清楚訊息**: Commit message 和組員通知都要詳細
5. ✅ **立刻 Push**: Commit 後不要忘記 push

### 爬蟲組特別注意

**口訣:** 爬完 → 匯出 → Commit → Push → 通知

**快捷鍵:** `./scripts/crawler_upload_helper.sh` (全自動)

---

## 📞 疑問排解

**Q: 我不小心建立了 outfit_db_20251126.sql 怎麼辦?**

A: 刪除它,重新匯出到正確檔名:
```bash
rm init/outfit_db_20251126.sql
./scripts/export_database.sh
```

**Q: 如果真的需要多個版本怎麼辦?**

A: 用 Git tag 或 branch:
```bash
# 建立重要里程碑標籤
git tag -a v1.0 -m "第一版:包含 50,000 筆商品"
git push origin v1.0

# 查看歷史標籤
git tag -l
```

**Q: 檔案太大 (超過 100 MB) 怎麼辦?**

A: 
1. 使用 Git LFS
2. 或改用雲端分享 (Google Drive/OneDrive)
3. 目前 8.2 MB,還不需要擔心

---

**最後更新:** 2025-11-26  
**維護者:** liaoyiting
