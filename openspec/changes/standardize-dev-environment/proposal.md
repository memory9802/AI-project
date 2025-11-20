# Change: 標準化開發環境配置管理

## Why

目前團隊開發面臨的核心問題：
- 組員因本機環境差異需要修改 `docker-compose.yml` 等核心配置檔案
- 修改後的核心檔案容易意外提交到 Git，影響其他組員的開發環境
- 缺乏統一的環境配置標準，導致每個組員都有自己的「適應版本」
- 無法確保所有組員使用相同的底層架構，增加部署和除錯困難

## What Changes

- **配置分離架構**：將核心配置與個人配置明確分離
  - 核心配置：團隊共用，版本控制，不允許個人修改
  - 本機配置：個人專屬，不納入版本控制，用於環境適配
- **Docker Compose Override 機制**：使用 `docker-compose.override.yml` 處理個人環境差異
- **環境變數標準化**：統一 `.env` 檔案管理和最佳實踐
- **開發工具整合**：VS Code 設定同步，確保開發體驗一致
- **文檔和指引**：提供跨平台（macOS/Windows）標準化設置指南

## Impact

- **受影響的規格**：dev-environment（新增）
- **受影響的檔案**：
  - `docker-compose.yml`（核心配置，鎖定版本）
  - `docker-compose.override.yml.example`（新增，個人配置範本）
  - `.env.example`（增強跨平台指引）
  - `.gitignore`（新增忽略規則）
  - `docs/DEVELOPMENT_SETUP.md`（新增設置指南）
  - `.vscode/settings.json`（新增，團隊開發設定）
- **團隊工作流程**：建立標準化的環境設置和維護流程
- **Git 管理**：清晰區分可提交和不可提交的配置檔案