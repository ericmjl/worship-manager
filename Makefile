run:
	bash activate.sh
	python run.py

dockerbuild:
	docker build data/. -t ericmjl/worshipdata
	docker build . -t ericmjl/worship

dockerrun:
	docker-compose up

dockerpush:
	echo "Assumes your Docker username is ericmjl! Hit Ctrl+C if this isn't true."
	# docker login
	docker tag ericmjl/worship ericmjl/worship
	docker push ericmjl/worship
	docker tag ericmjl/worshipdata ericmjl/worshipdata
	docker push ericmjl/worshipdata

start: dockerbuild dockerrun

push: dockerbuild dockerpush

test:
	bash activate.sh
	py.test --cov --cov-report term-missing -v
