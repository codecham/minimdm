.PHONY: help setup build start stop restart logs migrate seed flush shell bash test urls

GREEN  := \033[0;32m
YELLOW := \033[0;33m
CYAN   := \033[0;36m
WHITE  := \033[0;37m
BOLD   := \033[1m
RESET  := \033[0m

help:
	@echo ""
	@echo "$(BOLD)MiniMDM - Available commands$(RESET)"
	@echo "=============================="
	@echo ""
	@echo "$(YELLOW)Setup & Installation:$(RESET)"
	@echo "  $(CYAN)make setup$(RESET)      - First time setup (build + migrate + seed)"
	@echo "  $(CYAN)make build$(RESET)      - Rebuild containers"
	@echo ""
	@echo "$(YELLOW)Start & Stop:$(RESET)"
	@echo "  $(CYAN)make start$(RESET)      - Start containers"
	@echo "  $(CYAN)make stop$(RESET)       - Stop containers"
	@echo "  $(CYAN)make restart$(RESET)    - Restart containers"
	@echo "  $(CYAN)make logs$(RESET)       - View logs (Ctrl+C to exit)"
	@echo ""
	@echo "$(YELLOW)Database:$(RESET)"
	@echo "  $(CYAN)make migrate$(RESET)    - Run migrations"
	@echo "  $(CYAN)make seed$(RESET)       - Seed database with test data"
	@echo "  $(CYAN)make flush$(RESET)      - Clear all data from database"
	@echo ""
	@echo "$(YELLOW)Development:$(RESET)"
	@echo "  $(CYAN)make shell$(RESET)      - Open Django shell"
	@echo "  $(CYAN)make bash$(RESET)       - Open bash in web container"
	@echo "  $(CYAN)make test$(RESET)       - Run tests"
	@echo ""
	@echo "$(YELLOW)Utilities:$(RESET)"
	@echo "  $(CYAN)make urls$(RESET)       - Show useful URLs"
	@echo ""

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================

setup:
	@echo ""
	@echo "$(BOLD)Setting up MiniMDM...$(RESET)"
	@echo "====================="
	@echo ""
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env file from .env.example...$(RESET)"; \
		cp .env.example .env; \
		echo "$(GREEN)Done!$(RESET)"; \
		echo ""; \
	fi
	@echo "$(YELLOW)Building and starting containers...$(RESET)"
	@docker-compose up -d --build
	@echo ""
	@echo "$(YELLOW)Waiting for database to be ready...$(RESET)"
	@sleep 3
	@echo ""
	@echo "$(YELLOW)Running migrations...$(RESET)"
	@docker-compose exec web python manage.py migrate
	@echo ""
	@echo "$(YELLOW)Seeding database with test data...$(RESET)"
	@docker-compose exec web python manage.py seed_db --no-input
	@echo ""
	@echo "$(GREEN)$(BOLD)Setup complete!$(RESET)"
	@echo ""
	@make urls

build:
	@echo "$(YELLOW)Building containers...$(RESET)"
	@docker-compose build

# =============================================================================
# START & STOP
# =============================================================================

start:
	@echo "$(YELLOW)Starting containers...$(RESET)"
	@docker-compose up -d
	@echo ""
	@make urls

stop:
	@echo "$(YELLOW)Stopping containers...$(RESET)"
	@docker-compose down

restart:
	@echo "$(YELLOW)Restarting containers...$(RESET)"
	@docker-compose restart
	@echo ""
	@make urls

logs:
	@docker-compose logs -f web

# =============================================================================
# DATABASE
# =============================================================================

migrate:
	@echo "$(YELLOW)Running migrations...$(RESET)"
	@docker-compose exec web python manage.py migrate

seed:
	@echo "$(YELLOW)Seeding database...$(RESET)"
	@docker-compose exec web python manage.py seed_db

flush:
	@echo "$(YELLOW)Flushing database...$(RESET)"
	@docker-compose exec web python manage.py flush --no-input
	@echo "$(GREEN)Done! Database is now empty.$(RESET)"

# =============================================================================
# DEVELOPMENT
# =============================================================================

shell:
	@docker-compose exec web python manage.py shell

bash:
	@docker-compose exec web bash

test:
	@echo "$(YELLOW)Running tests...$(RESET)"
	@docker-compose exec web pytest

# =============================================================================
# UTILITIES
# =============================================================================

urls:
	@echo ""
	@echo "$(BOLD)Useful URLs:$(RESET)"
	@echo "  $(CYAN)API:$(RESET)      http://localhost:8000/api/"
	@echo "  $(CYAN)Swagger:$(RESET)  http://localhost:8000/api/docs/"
	@echo "  $(CYAN)ReDoc:$(RESET)    http://localhost:8000/api/redoc/"
	@echo "  $(CYAN)Admin:$(RESET)    http://localhost:8000/admin/"
	@echo "  $(CYAN)pgweb:$(RESET)    http://localhost:8081/"
	@echo ""
	@echo "$(BOLD)Test accounts:$(RESET)"
	@echo "  $(GREEN)admin$(RESET) / admin123  (admin user)"
	@echo "  $(GREEN)alice$(RESET) / alice123  (regular user with 2 fleets)"
	@echo "  $(GREEN)bob$(RESET)   / bob123    (regular user with 2 fleet)"
	@echo ""
