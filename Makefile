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

<<<<<<< HEAD
sync:
	bash sync.sh
=======
backup:
	docker save ericmjl/worshipdata:latest | gzip -c > ~/worshipdata.tgz
	docker load < ~/worshipdata.tgz
	docker tag ericmjl/worshipdata ericmjl/worshipdata
	docker push ericmjl/worshipdata
>>>>>>> 574be453a3c61ca98ac0c150dce422c728ed1dcc
