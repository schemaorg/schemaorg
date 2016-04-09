
# Makefile for docker templating

default: build

setup:
	pip install jinja2

build:
	python _build.py --all
	GIT_PAGER= git diff .

test-all:
	build-docker \
	run-docker-background \
	run-docker-background-test \
	run-docker-interactive

## Docker

project_orgname=schemaorg
project_name=schemaorg

os=Ubuntu
osrelease=15.04
#docker_tag_prefix=
docker_tag_prefix=$(project_name):
docker_tag_suffix=
DOCKERFILE=Dockerfile.$(os)-$(osrelease)
DOCKER_REPOTAG=$(docker_tag_prefix)$(os)-$(osrelease)$(docker_tag_suffix)
_USER=app
#DOCKER_BUILD_ARGS=--build-arg GITURL=$(GITURL) \
#                  --build-arg GITREV=$(GITREV)
DOCKER_BUILD_ARGS=
DOCKER_RUN_ARGS=-p 8000:8000 -p 8080:8080 -p 2222:22 -u '$(_USER)'

build-docker:
	docker build -f $(DOCKERFILE) -t $(DOCKER_REPOTAG) $(DOCKER_BUILD_ARGS) \
		.

run-docker-interactive-bash:
	docker run -i $(DOCKER_RUN_ARGS) -t $(DOCKER_REPOTAG) \
		/bin/bash -i

run-docker-interactive-dev_appserver:
	docker run -i $(DOCKER_RUN_ARGS) -t $(DOCKER_REPOTAG) \
		make dev_appserver

run-docker-background-init:
	docker run $(DOCKER_RUN_ARGS) -t $(DOCKER_REPOTAG) \
		/sbin/init

run-docker-background-dev_appserver:
	docker run $(DOCKER_RUN_ARGS) -t $(DOCKER_REPOTAG) \
		make dev_appserver

PIP='$(shell which pip)'
PIP_OPTS=

install_pipsi:
	@# install pipsi
	$(PIP) $(PIP_OPTS) pipsi

## docker-compose
DOCKER_COMPOSE="${HOME}/.local/bin/docker-compose"
# DOCKER_COMPOSE_VERSION=1.6.0
# | Download: https://github.com/docker/compose/releases
install_docker_compose:
	@# install docker-compose in a virtualenv and link to
	@# ~/.local/bin/docker-compose.yml
	which docker-compose \
		|| $(PIP) install $(PIP_OPTS) pipsi &&
		pipsi install docker-compose
	@#curl -L https://github.com/docker/compose/releases/download/$(DOCKER_COMPOSE_VERSION)/docker-compose-`uname -s`-`uname -m` > $(DOCKER_COMPOSE)
	@#chmod +x $(DOCKER_COMPOSE)
	
