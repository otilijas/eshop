# Django REST framework

![Python](https://img.shields.io/badge/python-v3.10-informational)
![Postgres](https://img.shields.io/badge/postgres-14-informational)
![Django](https://img.shields.io/badge/Django-latest-informational)
![DRF](https://img.shields.io/badge/DRF-latest-informational)
![OpenAPI](https://img.shields.io/badge/OpenAPI-v3-informational)

This is a simple project for showing the basics of building a minimal eshop API with DRF.
Users are able to view products and product's details, rate them, add items to cart and make a purchase.

## OpenAPI documentation

Documentation dynamically generated with OpenAPI3. It can be reached:

- `/schema/swagger/` for Swagger UI
- `/schema/redoc/` for ReDoc UI

## Getting started
### Docker

For Mac users - install latest [Docker Desktop](https://docs.docker.com/desktop/mac/install/)
For non-mac install docker and docker-compose system.

Clone project and start using:

```sh
make docker-run
```
Django server will start at http://localhost:8000 for local development. All migrations will be applied.

### Wrapped commands
The most common commands for this project are packed in universal wrapper:
```shell script
$ make help
make install         - install requirements.txt
make tools           - makes sure check-tools are present in environment
make super           - creates superuser with u:test, p:test
make mypy            - runs MyPy
make flake8          - runs Flake8
make test            - runs all tests
make check           - runs all tests and linters
make migrations      - runs django makemigrations command
make migrate         - applies django migrations
make shell           - starts interactive django shell
make docker-down     - stops docker containers and removes them
make docker-run      - starts django docker environment
```

### Environment management
How to use make command within docker:
```shell script
$ make run-docker
/eshop $ make mypy
mypy app mypy
Success: no issues found in 37 source files
/eshop $ 
```

## Project dependencies

Dependencies are stored in `requirements.txt`.
