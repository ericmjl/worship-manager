run:
	python run.py

dockerbuild:
	docker build . -t worship

dockerrun:
	docker run -p 8080:8080 -v worshipdata:/worship-manager/data worship

start: dockerbuild dockerrun
