all:
	docker-compose up --build

detach:
	docker-compose up --build --detach

test:
	docker exec backend pytest -s

down:
	docker-compose down

re: down
	docker-compose up --build --detach

clean: down
	docker-compose down --remove-orphans

fclean:
	docker-compose down --volumes --remove-orphans
	docker volume prune --force
	docker network prune --force
	docker system prune --force

.PHONY: all detach test down re clean fclean