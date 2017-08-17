run:
	python run.py

dockerbuild:
	docker build data/. -t ericmjl/worshipdata
	docker build . -t ericmjl/worship

dockerrun:
	# docker run \
	# 	-d \
	# 	--volumes-from worshipdata \
	# 	--restart always \
	# 	-p 9000:8080 \
	# 	-p 8888:8888 \
	# 	worship

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
	py.test --cov --cov-report term-missing -v
