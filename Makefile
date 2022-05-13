VIRTUAL_ENV_PATH=venv
SKIP_VENV="${NO_VENV}"

SHELL := /bin/bash

PYPI_API_KEY :=
PYPI_REPOSITORY_URL :=
ALPHA_VERSION :=
SRC_ROOT := ./src/hidlroute
PYTHON := python3

.DEFAULT_GOAL := pre_commit

pre_commit: copyright format lint
setup: venv deps create-dev-db

copyright:
	@( \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Applying copyright..."; \
       ./development/copyright-update; \
       echo "DONE: copyright"; \
    )

flake8:
	@( \
       set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Running Flake8 checks..."; \
       flake8 $(SRC_ROOT) --count --statistics; \
       echo "DONE: Flake8"; \
    )

mypy:
	@( \
       set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Running MyPy checks..."; \
       mypy --show-error-codes $(SRC_ROOT); \
       \
       echo "DONE: MyPy"; \
    )

format:
	@( \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Running Black code formatter..."; \
       black $(SRC_ROOT); \
       \
       echo "DONE: Black"; \
    )

check-format:
	@( \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Running Black format check..."; \
       black --check $(SRC_ROOT); \
       \
       echo "DONE: Black format check"; \
    )
	

lint: flake8 check-format

build: copyright format lint clean
	@( \
	   set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Building wheel package..."; \
       bash -c "cd src && VERSION_OVERRIDE="$(ALPHA_VERSION)" python ./setup.py bdist_wheel --dist-dir=../dist --bdist-dir=../../build"; \
       echo "DONE: wheel package"; \
    )
	@( \
	   set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       echo "Building source distribution..."; \
       bash -c "cd src && VERSION_OVERRIDE="$(ALPHA_VERSION)" python ./setup.py sdist --dist-dir=../dist"; \
       echo "DONE: source distribution"; \
    )

clean:
	@(rm -rf src/build dist/* *.egg-info src/*.egg-info .pytest_cache)

publish:
	@( \
       set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       if [ ! -z $(PYPI_API_KEY) ]; then export TWINE_USERNAME="__token__"; export TWINE_PASSWORD="$(PYPI_API_KEY)"; fi; \
       if [ ! -z $(PYPI_REPOSITORY_URL) ]; then  export TWINE_REPOSITORY_URL="$(PYPI_REPOSITORY_URL)"; fi; \
       echo "Uploading to PyPi"; \
       twine upload -r pypi dist/*; \
       echo "DONE: Publish"; \
    )

docker:
	@( \
       set -e; \
       if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
       if [ -z $(TAG) ]; then TAG="dev"; echo "Missing TAG argument defaulting to $$TAG"; fi; \
       echo "Building docker image hidlroute:$$TAG..."; \
       VERSION=`development/get-version.sh`; \
       RELEASE_DATE=`TZ="Europe/Kiev" date +%Y-%m-%d`; \
       docker build -t hidlroute:$$TAG --build-arg "VERSION=$$VERSION" --build-arg "RELEASE_DATE=$$RELEASE_DATE" . ; \
       echo "DONE: Docker Build"; \
    )

set-version:
	@( \
		if [ -z $(VERSION) ]; then echo "Missing VERSION argument"; exit 1; fi; \
		echo '__version__ = "$(VERSION)"' > $(SRC_ROOT)/__version__.py; \
		echo "Version updated: $(VERSION)"; \
	)

get-version:
	@( \
		development/get-version.sh; \
	)

deps:
	@( \
		source ./venv/bin/activate; \
		$(PYTHON) -m pip install -r ./requirements-dev.txt; \
	)

venv:
	@( \
		$(PYTHON) -m venv $(VIRTUAL_ENV_PATH); \
		source ./venv/bin/activate; \
	)

db: delete-db create-dev-db

migrate:
	@( \
        if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
        echo "Applying migrations."; \
        $(PYTHON) src/manage.py migrate; \
	)

create-superuser:
	@( \
        if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
        echo "Applying migrations..."; \
        $(PYTHON) src/manage.py migrate; \
        echo "Creating superuser..."; \
        DJANGO_SUPERUSER_PASSWORD=demoadmin $(PYTHON) src/manage.py createsuperuser --username=demoadmin --email=admin@demo.com  --no-input; \
	)

create-dev-db: migrate create-superuser load-dataset
delete-db:
	@( \
        if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
        echo "Deleting database..."; \
        if [ -f "./dev-data/db.sqlite3" ]; then rm ./dev-data/db.sqlite3; echo "  DONE"; else echo "  Database doesn't exist"; fi; \
	)

load-dataset:
	@( \
        if [ -z $(SKIP_VENV) ]; then source $(VIRTUAL_ENV_PATH)/bin/activate; fi; \
        echo "Loading dataset..."; \
#        $(PYTHON) src/manage.py loaddata <NAME>; \
	)

dev-containers:
	@( \
		echo "Starting docker containers"; \
		docker-compose -f dev-containers.yaml up -d; \
		echo "DONE: Docker containers started"; \
	)