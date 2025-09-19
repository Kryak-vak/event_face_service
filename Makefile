SERVICE_NAME = web
DOCKER_RUN = docker compose run $(SERVICE_NAME)
DOCKER_EXEC = docker compose exec -it


build:
	docker compose build

clean:
	docker image prune -f

up: build
	docker compose up --watch

down:
	docker compose down --remove-orphans
	$(MAKE) clean

reload: down up

restart: 
	docker compose restart $(SERVICE_NAME)

logs:
	docker compose logs $(SERVICE_NAME)


test: build
	$(DOCKER_RUN) uv run pytest


migrations: 
#           build
	$(DOCKER_RUN) uv run manage.py makemigrations
# 	uv run manage.py makemigrations
	
migrate:
	$(DOCKER_RUN) uv run manage.py migrate
# 	uv run manage.py migrate

automigrate: migrations migrate

shema:
	uv run manage.py spectacular --color --file schema.yml
	docker run --rm -p 8080:8080 \
		-e SWAGGER_JSON=/schema.yml \
		-v $(PWD)/schema.yml:/schema.yml \
		swaggerapi/swagger-ui

docker_shell:
	$(DOCKER_EXEC) web bash

dbshell:
	$(DOCKER_EXEC) db psql -U postgres


format:
	uv run ruff format src/

check:
	uv run ruff check src/
	uv run mypy src/

pip_fix:
	.\backend\.venv\Scripts\python.exe -m ensurepip --upgrade
	.\backend\.venv\Scripts\python.exe -m pip install --upgrade pip setuptools wheel

