test:
	py.test --cov --cov-report term-missing -v

run:
	python run.py

build:
	docker build data/. -t ericmjl/worshipdata
	docker build . -t ericmjl/worship

start:
	docker-compose up

push:
	docker tag ericmjl/worship ericmjl/worship
	docker push ericmjl/worship
	docker tag ericmjl/worshipdata ericmjl/worshipdata
	docker push ericmjl/worshipdata

# start: dockerbuild dockerrun

# push: dockerbuild dockerpush
