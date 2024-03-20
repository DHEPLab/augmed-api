.PHONY: start
start: install run

.PHONY: install
install:
	pip3 install pipenv
	pipenv --python `which python3`
	pipenv install

.PHONY: run
run: install
	sh -c ' \
		export PYTHONPATH=`pwd` && \
		if [ ! -f .env ]; then cp .env.temp .env; fi && \
		echo $(PYTHONPATH) && \
		docker-compose up -d db && \
		python3 src/app.py \
	'

.PHONY: format
format: install
	pipenv run black src


.PHONY: lint
lint: install
	pipenv run flake8 src

.PHONY: test
test: install
	sh -c ' \
		export DOCKER_HOST=unix://$(HOME)/.colima/default/docker.sock && \
		pipenv run pytest tests \
	'

.PHONY: clean
clean:
	pipenv --rm
	docker stop postgres_container
