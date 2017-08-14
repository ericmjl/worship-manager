run:
	python run.py

dockerbuild:
	docker build . -t worship

dockerrun:
	docker run -p 8080:8080 -v worshipdata:/worship-manager/data worship

dockerupload:
	echo "Assumes your username is ericmjl! Hit Ctrl+C if this isn't true."
	docker login
	docker tag worship ericmjl/worship
	docker push ericmjl/worship

start: dockerbuild dockerrun

test:
	py.test --cov --cov-report term-missing
