.PHONY: test # @see https://stackoverflow.com/a/3931814

# @see https://krzysztofzuraw.com/blog/2016/makefiles-in-python-projects.html
# @see https://medium.com/@hmajid2301/implementing-sqlalchemy-with-docker-cb223a8296de
ENV_FILE = $$([ -f "$(shell pwd)/.env" ] && printf "%s" "$(shell pwd)/.env" || printf "%s" "$(shell pwd)/.env.dist")
MODE = $$(. $(ENV_FILE); printf "%s" "$${FLASK_ENV}")
TARGET = $$(. $(ENV_FILE); printf "%s" "$${FLASK_TARGET}")
TARGET_ADMINER = `case "$(TARGET)" in \
	*mariadb*) printf "%s" "server";; \
	*mssql*) printf "%s" "mssql";; \
	*mysql*) printf "%s" "server";; \
	*oracle*) printf "%s" "oracle";; \
	*postgres*) printf "%s" "pgsql";; \
	*) printf "%s\n" "Error, no valid target found!" 1>&2;; esac`#TODO: add sqlite, mongodb, elasticsearch...
CONTAINER = `docker ps | grep $(TARGET) | xargs -n1 2>/dev/null | head -n1`
CONTAINER_ADMINER = `docker ps | grep adminer | xargs -n1 2>/dev/null | head -n1`
INSPECT = `docker image inspect $(TARGET) 2>/dev/null | sed ':a;N;$!ba;s/\n//g'`
INTERFACE = $$(docker exec --interactive --tty $(CONTAINER) ip route | grep default | awk '{print $$5}')
IP = $$(docker exec --interactive --tty $(CONTAINER) ip -4 addr show $(INTERFACE) | grep inet | awk '{print $$2}' | awk -F"/" '{print $$1}')
IP_ADMINER = $$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(CONTAINER_ADMINER))
NET = $$([ ! "$$(command -v "docker-machine")" ] && printf "%s" "$(IP)" || docker-machine ip default)
NET_ADMINER = $$([ ! "$$(command -v "docker-machine")" ] && printf "%s" "$(IP_ADMINER)" || docker-machine ip default)
#PATH := $$([ "$(shell uname)" = "Linux" ] && printf "%s:%s" "$(PATH)" "$(HOME)/.local/bin" || printf "%s" "$(PATH)")
PIP_PREFIX = $$([ ! "$$(command -v "python3")" ] && printf "%s" "python" || printf "%s" "python3")
PIP_PREPARE = $(PIP_PREFIX) -m pip install --user gunicorn pythonloc tox
PIP_REQUIRE = piploc install -r "requirements/prod.txt"
PIP_REQ_DEV = piploc install -r "requirements/dev.txt"
PIP_RUN = pipx run --pypackages
PORT = $$(docker inspect -f '{{.Config.ExposedPorts}}' $(TARGET) | sed 's/map\[\([0-9]*\)\/.*/\1/')
PORT_ADMINER = $$(docker inspect -f '{{.Config.ExposedPorts}}' adminer | sed 's/map\[\([0-9]*\)\/.*/\1/')
#SHELL := /usr/bin/env bash # @see https://stackoverflow.com/a/43566158
STAMP = $$(printf "%s_%s" "$$(printf "%s" "$(TARGET)" | cut -d: -f1 | cut -d/ -f2)" "$$(date +"%Y-%m-%d_%H-%M-%S")")

babel-compile:
	$(PIP_RUN) pybabel compile --directory=translations

babel-extract:
	$(PIP_RUN) pybabel extract --mapping-file=babel.cfg --output-file=translations/messages.pot .

babel-install:
	$(PIP_RUN) pybabel init --input-file=translations/messages.pot --output-dir=translations --locale=es
	$(PIP_RUN) pybabel init --input-file=translations/messages.pot --output-dir=translations --locale=eu
	$(PIP_RUN) pybabel init --input-file=translations/messages.pot --output-dir=translations --locale=fr

babel-update:
	$(PIP_RUN) pybabel update --input-file=translations/messages.pot --output-dir=translations

clean:
	find . -name '*.pyc' -exec rm --force --verbose {} +
	find . -name '*.pyo' -exec rm --force --verbose {} +
	find . -name '*~' -exec rm --force --verbose {} +
	find . -name '.parcel-cache' -exec rm --force --recursive --verbose {} +
	find . -name '.pytest_cache' -exec rm --force --recursive --verbose {} +
	find . -name '__pycache__' -exec rm --force --recursive {} +

clean-adminer: stop-adminer
	# @see https://success.docker.com/article/how-to-remove-a-signed-image-with-a-none-tag
	#docker images --digests adminer
	docker rmi --force adminer

clean-all: stop-all clean
	yes | docker system prune -a

clean-all-volumes: stop-all clean
	yes | docker system prune -a --volumes

clean-db:
	$(PIP_RUN) flask ps drop

clean-target: stop-target
	[ "$(INSPECT)" = "[]" ] || docker rmi $(TARGET)

designer:
	[ "$(MODE)" = "development" ] && $(PIP_RUN) designer || printf "%s" "ERROR: Designer requires development environment."

env:
	printf "%s" "$(MODE)"

freeze:
	# @see https://medium.com/@grassfedcode/goodbye-virtual-environments-b9f8115bc2b6
	pipfreezeloc | tr 'A-Z' 'a-z' | sort

help:
	$(PIP_RUN) flask --help

help-db:
	$(PIP_RUN) flask db --help

help-ps:
	$(PIP_RUN) flask ps --help

install:
	$(PIP_PREPARE)
	npm --prefix assets install
	[ "$(MODE)" = "development" ] && $(PIP_REQ_DEV) | tee || $(PIP_REQUIRE) | tee

ip: start-target
	printf "%s" "$(NET)"

lint:
	[ "$(MODE)" = "development" ] && ($(PIP_RUN) flask lint --fix-imports || exit 0) || printf "%s" "ERROR: Linter requires development environment."

list:
	docker ps --size

log-adminer:
	docker-compose logs | grep adminer || exit 0

log-target:
	[ -z "$(CONTAINER)" ] || docker logs $(CONTAINER)

parcel-build:
	npm --prefix assets run build

parcel-start:
	npm --prefix assets run start

port: start-target
	printf "%s" "$(PORT)"

routes:
	$(PIP_RUN) flask routes

run:
	$(PIP_RUN) flask run --with-threads

shell:
	$(PIP_RUN) flask shell

shell-adminer: start-adminer
	docker exec --interactive --tty $(CONTAINER_ADMINER) sh

shell-target: start-target
	docker exec --interactive --tty $(CONTAINER) sh

start: start-target parcel-build babel-compile run

start-adminer: start-target
	[ -z "$(CONTAINER_ADMINER)" ] && docker-compose up --detach --no-recreate --remove-orphans adminer || exit 0
	[ -z "$(CONTAINER_ADMINER)" ] || printf "adminer is running at http://%s:%s/?%s=%s\n" "$(NET_ADMINER)" "$(PORT_ADMINER)" "$(TARGET_ADMINER)" "$(NET)"

start-target:
	[ -z "$(CONTAINER)" ] && docker pull $(TARGET) || exit 0
	#TODO: add --volume
	#TODO: remove --name & --publish
	[ -z "$(CONTAINER)" ] && docker run --detach --env-file $(ENV_FILE) --hostname $(STAMP) --name $(STAMP) --network host --publish $(PORT):$(PORT) --rm $(TARGET) || exit 0
	[ -z "$(CONTAINER)" ] || printf "%s is running at http://%s:%s\n" "$(TARGET)" "$(NET)" "$(PORT)"

start-ui: start-target parcel-build babel-compile ui

stop-adminer:
	docker-compose stop adminer

stop-all:
	#TODO: shutdown werkzeug
	docker stop `docker ps -q` 2>/dev/null || exit 0

stop-target:
	[ -z "$(CONTAINER)" ] || docker stop $(CONTAINER)

test:
	$(PIP_PREFIX) tests/main_tests.py

ui:
	$(PIP_PREFIX) src/main.py

update:
	$(PIP_PREFIX) -m pip install --upgrade pip
	$(PIP_PREPARE) --upgrade
	npm --prefix assets upgrade
	[ "$(MODE)" = "development" ] && $(PIP_REQ_DEV) --upgrade | tee || $(PIP_REQUIRE) --upgrade | tee
