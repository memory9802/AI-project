## Purpose

本規格定義 AI 穿搭推薦專案的標準化開發環境配置管理需求，旨在解決團隊協作中因環境差異導致的問題。透過建立配置分離架構、VS Code 統一設定、Git 保護策略和自動化檢查工具，確保所有團隊成員使用一致的開發環境，提升協作效率並降低環境相關的問題發生率。

## Requirements

### Requirement: 核心配置版本鎖定
系統 SHALL 維護不可修改的核心配置檔案，確保所有團隊成員使用相同的底層架構。

#### Scenario: 核心配置保護
- **WHEN** 團隊成員嘗試修改 `docker-compose.yml` 核心配置
- **THEN** 系統應提供替代方案（override 檔案）而非允許修改核心檔案
- **AND** Git 提交檢查應警告核心配置的變更

#### Scenario: 架構一致性驗證  
- **WHEN** 開發者建立開發環境
- **THEN** 所有容器服務（MySQL、Flask、phpMyAdmin）的基礎配置必須相同
- **AND** 資料庫結構和API端點保持一致

### Requirement: 個人環境適配機制
系統 MUST 提供標準化的個人環境適配方式，不影響核心架構。

#### Scenario: Docker Compose Override 使用
- **WHEN** 開發者需要調整端口映射或資料卷路徑
- **THEN** 應使用 `docker-compose.override.yml` 檔案進行個人適配
- **AND** Override 檔案不應被提交到版本控制

#### Scenario: 跨平台環境適配
- **WHEN** macOS 或 Windows 開發者設置環境
- **THEN** 應提供平台特定的配置範本和指引
- **AND** 個人適配不應影響其他平台的開發者

### Requirement: 環境變數安全管理
系統 SHALL 實施分層的環境變數管理，保護敏感資訊並標準化配置。

#### Scenario: API 金鑰保護
- **WHEN** 開發者配置 AI API 金鑰
- **THEN** 實際金鑰應存儲在 `.env` 檔案中且不被提交到 Git
- **AND** 應提供 `.env.example` 作為配置範本

#### Scenario: 環境變數驗證
- **WHEN** 應用程式啟動時
- **THEN** 應檢查必要的環境變數是否正確設置
- **AND** 缺少配置時應提供清晰的錯誤訊息和解決指引

### Requirement: 開發工具標準化
系統 SHALL 提供統一的開發工具配置，維持程式碼品質一致性。

#### Scenario: VS Code 設定同步
- **WHEN** 團隊成員使用 VS Code 開發
- **THEN** 應自動套用統一的格式化設定（Python PEP 8、JavaScript）
- **AND** 應建議安裝相關的開發擴充套件

#### Scenario: 除錯配置標準化
- **WHEN** 開發者需要除錯應用程式
- **THEN** 應提供預配置的除錯設定檔（`.vscode/launch.json`）
- **AND** 支援 Docker 容器內的除錯功能

### Requirement: 環境設置驗證
系統 MUST 提供自動化的環境設置驗證機制。

#### Scenario: 環境健康檢查
- **WHEN** 開發者完成環境設置
- **THEN** 應能執行自動化檢查腳本驗證配置正確性
- **AND** 檢查結果應包含具體的修復建議

#### Scenario: 依賴項目驗證
- **WHEN** 執行環境檢查
- **THEN** 應驗證 Docker、Node.js、Python 等關鍵依賴的版本
- **AND** 檢查必要的端口（5001、3306、8080）是否可用

### Requirement: 文檔和指引完整性
系統 SHALL 提供完整且整合的跨平台開發環境設置文檔。

#### Scenario: 新手設置指引
- **WHEN** 新團隊成員加入專案
- **THEN** 應提供step-by-step的環境設置指南
- **AND** 包含 macOS 和 Windows 的具體操作步驟

#### Scenario: 問題排除支援
- **WHEN** 開發者遇到環境配置問題
- **THEN** 文檔應包含常見問題和解決方案
- **AND** 提供故障排除的診斷流程

### Requirement: 文檔架構簡化
系統 MUST 整合分散的文檔，提供單一參考來源。

#### Scenario: 統一規格指南
- **WHEN** 團隊成員需要查詢開發規範
- **THEN** 應提供單一的 `SPEC_GUIDE.md` 整合所有相關資訊
- **AND** 包含 OpenSpec 工作流程、環境設置、團隊協作的完整指引

#### Scenario: 減少文檔維護負擔
- **WHEN** 專案資訊需要更新
- **THEN** 主要更新應集中在統一指南中
- **AND** 避免在多個文檔中重複維護相同資訊

### Requirement: OpenSpec 規格驗證
系統 SHALL 確保所有變更提案符合 OpenSpec 格式規範。

#### Scenario: 變更提案驗證
- **WHEN** 開發者創建 OpenSpec 變更提案
- **THEN** 應通過 `openspec validate --strict` 檢查
- **AND** 包含完整的 proposal.md、tasks.md 和相關規格

#### Scenario: 規格實作追蹤
- **WHEN** 功能開發完成
- **THEN** 應更新正式規格反映實際實作結果
- **AND** 歸檔變更提案以維護歷史記錄