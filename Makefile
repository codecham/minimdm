ifeq ($(OS),Windows_NT)
    SLEEP = timeout /t
else
    SLEEP = sleep
endif

.PHONY: help setup build start stop restart logs migrate seed flush shell bash test urls

help:
	@echo ""
	@echo "MiniMDM - Available commands"
	@echo "=============================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup      - First time setup (build + migrate + seed)"
	@echo "  make build      - Rebuild containers"
	@echo ""
	@echo "Start & Stop:"
	@echo "  make start      - Start containers"
	@echo "  make stop       - Stop containers"
	@echo "  make restart    - Restart containers"
	@echo "  make logs       - View logs (Ctrl+C to exit)"
	@echo ""
	@echo "Database:"
	@echo "  make migrate    - Run migrations"
	@echo "  make seed       - Seed database with test data"
	@echo "  make flush      - Clear all data from database"
	@echo ""
	@echo "Development:"
	@echo "  make shell      - Open Django shell"
	@echo "  make bash       - Open bash in web container"
	@echo "  make test       - Run tests"
	@echo ""
	@echo "Utilities:"
	@echo "  make urls       - Show useful URLs"
	@echo ""

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================

setup:
	@echo ""
	@echo "Setting up MiniMDM..."
	@echo "====================="
	@echo ""
	@echo "Building and starting containers..."
	@docker-compose up -d --build
	@echo ""
	@echo "Waiting for database to be ready (5s)..."
	@$(SLEEP) 5
	@echo ""
	@echo "Running migrations..."
	@docker-compose exec web python manage.py migrate
	@echo ""
	@echo "Seeding database with test data..."
	@docker-compose exec web python manage.py seed_db --no-input
	@echo ""
	@echo "Setup complete!"
	@echo ""
	@make urls

build:
	@echo "Building containers..."
	@docker-compose build

# =============================================================================
# START & STOP
# =============================================================================

start:
	@echo "Starting containers..."
	@docker-compose up -d
	@echo ""
	@make urls

stop:
	@echo "Stopping containers..."
	@docker-compose down

restart:
	@echo "Restarting containers..."
	@docker-compose restart
	@echo ""
	@make urls

logs:
	@docker-compose logs -f web

# =============================================================================
# DATABASE
# =============================================================================

migrate:
	@echo "Running migrations..."
	@docker-compose exec web python manage.py migrate

seed:
	@echo "Seeding database..."
	@docker-compose exec web python manage.py seed_db

flush:
	@echo "Flushing database..."
	@docker-compose exec web python manage.py flush --no-input
	@echo "Done! Database is now empty."

# =============================================================================
# DEVELOPMENT
# =============================================================================

shell:
	@docker-compose exec web python manage.py shell

bash:
	@docker-compose exec web bash

test:
	@echo "Running tests..."
	@docker-compose exec web pytest

# =============================================================================
# UTILITIES
# =============================================================================

urls:
	@echo ""
	@echo "Useful URLs:"
	@echo "  API:      http://localhost:8000/api/"
	@echo "  Swagger:  http://localhost:8000/api/docs/"
	@echo "  ReDoc:    http://localhost:8000/api/redoc/"
	@echo "  Admin:    http://localhost:8000/admin/"
	@echo "  pgweb:    http://localhost:8081/"
	@echo ""
	@echo "Test accounts:"
	@echo "  admin / admin123  (admin user)"
	@echo "  alice / alice123  (regular user with 2 fleets)"
	@echo "  bryan / bryan123  (regular user with 1 fleet)"
	@echo ""