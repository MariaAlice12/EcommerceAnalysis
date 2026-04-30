.PHONY: up down rebuild logs logs-all shell mysql reset

up:
	docker compose up -d
	@echo ""
	@echo "Aguarde ~90s para inicializar. Acesse: http://localhost:8088"
	@echo "Login: admin / admin"

down:
	docker compose down

rebuild:
	docker compose down
	docker compose build --no-cache
	docker compose up -d

logs:
	docker compose logs -f superset

logs-all:
	docker compose logs -f

shell:
	docker exec -it superset_app bash

mysql:
	docker exec -it superset_mysql mysql -u superset -psupersetpass ecommerce

reset:
	docker compose down -v
	docker compose build --no-cache
	docker compose up -d
