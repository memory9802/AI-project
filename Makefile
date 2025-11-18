# AI-Project Makefile
# 提供簡單的指令來管理不同環境

# 預設配置
.DEFAULT_GOAL := help

# 顏色定義
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
NC := \033[0m # No Color

.PHONY: help
help: ## 顯示幫助訊息
	@echo "$(BLUE)AI-Project 管理指令$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

.PHONY: dev-a
dev-a: ## 啟動開發環境 A (port 5001, 8080)
	@echo "$(YELLOW)啟動開發環境 A...$(NC)"
	FLASK_PORT=5001 MYSQL_PORT=3306 PHPMYADMIN_PORT=8080 CONTAINER_PREFIX=dev-a docker-compose up -d
	@echo "$(GREEN)✓ 開發環境 A 已啟動$(NC)"
	@echo "Flask: http://localhost:5001"
	@echo "phpMyAdmin: http://localhost:8080"

.PHONY: dev-b
dev-b: ## 啟動開發環境 B (port 5002, 8081)
	@echo "$(YELLOW)啟動開發環境 B...$(NC)"
	FLASK_PORT=5002 MYSQL_PORT=3307 PHPMYADMIN_PORT=8081 CONTAINER_PREFIX=dev-b docker-compose up -d
	@echo "$(GREEN)✓ 開發環境 B 已啟動$(NC)"
	@echo "Flask: http://localhost:5002"
	@echo "phpMyAdmin: http://localhost:8081"

.PHONY: dev-c
dev-c: ## 啟動開發環境 C (port 5003, 8082)
	@echo "$(YELLOW)啟動開發環境 C...$(NC)"
	FLASK_PORT=5003 MYSQL_PORT=3308 PHPMYADMIN_PORT=8082 CONTAINER_PREFIX=dev-c docker-compose up -d
	@echo "$(GREEN)✓ 開發環境 C 已啟動$(NC)"
	@echo "Flask: http://localhost:5003"
	@echo "phpMyAdmin: http://localhost:8082"

.PHONY: up
up: ## 使用 .env 設定啟動
	@echo "$(YELLOW)使用 .env 設定啟動...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ 服務已啟動$(NC)"

.PHONY: down
down: ## 停止所有服務
	@echo "$(YELLOW)停止服務...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ 服務已停止$(NC)"

.PHONY: restart
restart: ## 重啟服務
	@echo "$(YELLOW)重啟服務...$(NC)"
	docker-compose restart
	@echo "$(GREEN)✓ 服務已重啟$(NC)"

.PHONY: logs
logs: ## 查看 Flask 日誌
	docker logs outfit-flask --tail 50 -f

.PHONY: ps
ps: ## 查看運行中的容器
	docker-compose ps

.PHONY: ports
ports: ## 顯示所有容器的 port 映射
	@docker ps --format "table {{.Names}}\t{{.Ports}}" | grep outfit

.PHONY: clean
clean: ## 停止並清除所有資料（包含 volumes）
	@echo "$(YELLOW)⚠️  警告：這將刪除所有資料！$(NC)"
	@read -p "確定要繼續嗎? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		docker-compose down -v; \
		echo "$(GREEN)✓ 已清除所有資料$(NC)"; \
	else \
		echo "$(BLUE)已取消$(NC)"; \
	fi

.PHONY: build
build: ## 重新建構 Docker 映像
	@echo "$(YELLOW)重新建構映像...$(NC)"
	docker-compose build --no-cache
	@echo "$(GREEN)✓ 建構完成$(NC)"

.PHONY: shell
shell: ## 進入 Flask 容器的 shell
	docker exec -it outfit-flask bash

.PHONY: test
test: ## 測試服務是否正常
	@echo "$(YELLOW)測試服務...$(NC)"
	@curl -s http://localhost:5001/ping | grep -q "ok" && echo "$(GREEN)✓ Flask 正常運作$(NC)" || echo "$(YELLOW)✗ Flask 無法連線$(NC)"

# 使用範例：
# make dev-a      # 啟動開發環境 A
# make dev-b      # 啟動開發環境 B
# make ports      # 查看 port 映射
# make logs       # 查看日誌
# make down       # 停止服務
