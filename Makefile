.PHONY: prod-build prod-up prod-down logs backup

prod-build:
	docker compose -f docker-compose.prod.yml build

prod-up:
	docker compose -f docker-compose.prod.yml up -d

prod-down:
	docker compose -f docker-compose.prod.yml down

logs:
	docker compose -f docker-compose.prod.yml logs -f --tail 100

backup:
	bash scripts/backup_db.sh
