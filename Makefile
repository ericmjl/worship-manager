test:
	py.test --cov --cov-report term-missing -v

run:
	python run.py

build:
	docker build --no-cache . -t ericmjl/worship

start:
	docker-compose stop
	docker-compose rm -f
	docker-compose pull
	docker-compose up

push:
	docker tag ericmjl/worship ericmjl/worship
	docker push ericmjl/worship

pull:
	docker pull ericmjl/worship

sync:
	bash sync.sh
