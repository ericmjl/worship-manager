test:
	py.test --cov --cov-report term-missing -v

run:
	python run.py

build:
	docker build --no-cache data/. -t ericmjl/worshipdata
	docker build --no-cache . -t ericmjl/worship

start:
	docker-compose stop
	docker-compose rm -f
	docker-compose pull
	docker-compose up

push:
	docker tag ericmjl/worship ericmjl/worship
	docker push ericmjl/worship
	docker tag ericmjl/worshipdata ericmjl/worshipdata
	docker push ericmjl/worshipdata

pull:
	docker pull ericmjl/worship
	docker pull ericmjl/worshipdata

backup:
	docker save ericmjl/worshipdata:latest | gzip -c > ~/worshipdata.tgz
