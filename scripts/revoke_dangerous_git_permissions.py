#!/usr/bin/env python3
"""
撤回 VS Code Copilot 的危險 Git 操作授權

這個腳本會:
1. 備份當前設定
2. 移除危險的 git 自動授權
3. 保留安全的查詢類操作
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path

# VS Code 使用者設定檔路徑
SETTINGS_PATH = Path.home() / "Library/Application Support/Code/User/settings.json"

# 🚨 需要移除的危險授權 (會改變檔案版本/歷史)
DANGEROUS_PERMISSIONS = [
    "git reset",           # 🚨 可能執行 reset --hard
    "git push",            # 🚨 可能執行 push --force
    "git checkout",        # ⚠️ 可能丟失未提交變更
    "git merge",           # ⚠️ 可能造成合併衝突
    "git rm",              # ⚠️ 可能刪除重要檔案
    "git restore",         # ⚠️ 可能丟失變更
    "git rebase",          # 🚨 重寫提交歷史
    "git stash",           # ⚠️ 可能丟失變更
]

# ✅ 允許保留的安全操作 (只讀,不修改)
SAFE_PERMISSIONS = [
    "git status",
    "git log",
    "git diff",
    "git show",
    "git branch",         # 只列出分支 (不含 -D 刪除)
    "git fetch",          # 只取得資訊,不修改本地
    "git remote",         # 查看遠端資訊
    "git add",            # 暫存變更 (可恢復)
]

# ⚠️ 需要詢問確認的操作 (會修改但相對安全)
CONFIRM_REQUIRED = [
    "git commit",         # 提交到本地 (已在 GIT_WORKFLOW.md 中要求確認)
]

def main():
    print("🔐 撤回 VS Code Copilot 危險 Git 操作授權")
    print("=" * 60)
    
    # 檢查設定檔是否存在
    if not SETTINGS_PATH.exists():
        print(f"❌ 找不到設定檔: {SETTINGS_PATH}")
        return
    
    # 讀取設定檔
    print(f"\n📖 讀取設定檔: {SETTINGS_PATH}")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        settings = json.load(f)
    
    # 檢查是否有 autoApprove 設定
    if "chat.tools.terminal.autoApprove" not in settings:
        print("✅ 沒有發現自動授權設定,不需要修改")
        return
    
    auto_approve = settings["chat.tools.terminal.autoApprove"]
    
    # 分析當前授權
    print("\n🔍 分析當前授權:")
    dangerous_found = []
    safe_found = []
    
    for cmd in auto_approve.keys():
        cmd_str = str(cmd)
        is_dangerous = False
        
        for dangerous_cmd in DANGEROUS_PERMISSIONS:
            if cmd_str.startswith(dangerous_cmd):
                dangerous_found.append(cmd_str)
                is_dangerous = True
                break
        
        if not is_dangerous:
            for safe_cmd in SAFE_PERMISSIONS:
                if cmd_str.startswith(safe_cmd):
                    safe_found.append(cmd_str)
                    break
    
    print(f"  🚨 危險授權: {len(dangerous_found)} 個")
    for cmd in dangerous_found[:5]:  # 只顯示前 5 個
        print(f"     - {cmd}")
    if len(dangerous_found) > 5:
        print(f"     ... 還有 {len(dangerous_found) - 5} 個")
    
    print(f"  ✅ 安全授權: {len(safe_found)} 個")
    for cmd in safe_found[:3]:
        print(f"     - {cmd}")
    if len(safe_found) > 3:
        print(f"     ... 還有 {len(safe_found) - 3} 個")
    
    # 建立新的授權清單 (移除危險操作)
    print(f"\n🛡️ 移除 {len(dangerous_found)} 個危險授權...")
    new_auto_approve = {}
    removed_count = 0
    
    for cmd, value in auto_approve.items():
        cmd_str = str(cmd)
        should_remove = False
        
        for dangerous_cmd in DANGEROUS_PERMISSIONS:
            if cmd_str.startswith(dangerous_cmd):
                should_remove = True
                removed_count += 1
                break
        
        if not should_remove:
            new_auto_approve[cmd] = value
    
    # 更新設定
    settings["chat.tools.terminal.autoApprove"] = new_auto_approve
    
    # 額外關閉 git 自動同步 (以防萬一)
    if "git.confirmSync" in settings:
        print("🔒 啟用 Git 同步確認 (git.confirmSync: false -> true)")
        settings["git.confirmSync"] = True
    
    # 寫入新設定
    backup_path = SETTINGS_PATH.parent / f"settings.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(SETTINGS_PATH, backup_path)
    print(f"\n💾 備份原設定到: {backup_path.name}")
    
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    
    print(f"✅ 成功寫入新設定!")
    
    # 顯示摘要
    print("\n" + "=" * 60)
    print("📊 撤回授權摘要:")
    print(f"  ❌ 移除危險授權: {removed_count} 個")
    print(f"  ✅ 保留安全授權: {len(new_auto_approve)} 個")
    print("\n🔐 現在 Copilot 無法自動執行以下危險操作:")
    for cmd in DANGEROUS_PERMISSIONS:
        print(f"  ❌ {cmd}")
    
    print("\n✅ Copilot 仍可執行以下安全操作:")
    for cmd in SAFE_PERMISSIONS[:5]:
        print(f"  ✅ {cmd}")
    
    print("\n⚠️  需要手動確認的操作:")
    for cmd in CONFIRM_REQUIRED:
        print(f"  ⚠️  {cmd}")
    
    print("\n" + "=" * 60)
    print("✅ 授權撤回完成!")
    print("💡 請重新啟動 VS Code 使設定生效")
    print("\n🔗 相關文檔:")
    print("  - docs/VERSION_PROTECTION_POLICY.md")
    print("  - docs/GIT_WORKFLOW.md")

if __name__ == "__main__":
    main()
