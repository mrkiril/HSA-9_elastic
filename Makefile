MAIN_SERVICE = projector_service


up:
	docker-compose up -d
	docker-compose ps

run:
	docker-compose build --parallel --no-cache
	docker-compose up -d
	docker-compose ps

restart:
	docker-compose restart $(MAIN_SERVICE)
	docker-compose ps

rebuild:
	sudo -S rm -rf ./nginx_cache/*
	docker-compose build --parallel
	docker-compose up -d
	docker-compose ps


load_data:
