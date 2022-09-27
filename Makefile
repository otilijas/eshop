.PHONY: install tools super mypy flake8 test check migrations migrate run shell docker-down docker-run

help:
	@echo 'make install         - install requirements.txt.'
	@echo 'make tools           - makes sure check-tools are resent in environment.'
	@echo 'make super           - creates superuser with u:test, p:test.'
	@echo 'make mypy            - runs MyPy.'
	@echo 'make flake8          - runs Flake8'
	@echo 'make test            - runs tests.'
	@echo 'make check           - runs tests and other checks (Flake8 and MyPy).
	@echo 'make migrations      - runs django makemigrations command.'
	@echo 'make migrate         - applies django migrations.'
	@echo 'make run             - starts django server at http://localhost:8000 for local development.'
	@echo 'make shell           - starts interactive django shell.'
	@echo 'make docker-down     - stops docker containers and removes them'
	@echo 'make docker-run      - starts django docker environment'

install:
	pip install -r requirements.txt

tools:
	pip install pip-tools==6.2.0 pip==21.2.4

super:
	export DJANGO_SUPERUSER_EMAIL=test@test.com; export DJANGO_SUPERUSER_PASSWORD=test; python manage.py createsuperuser --username test --noinput

mypy:
	mypy app

flake8:
	flake8 app

test:
	python manage.py test app.tests

check: flake8 mypy test

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

run:
	python manage.py runserver 0.0.0.0:8000

shell:
	python manage.py shell

docker-down:
	docker-compose -f docker-compose.yml down

docker-run:
	docker-compose up
