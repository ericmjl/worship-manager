run:
	python run.py

dockerbuild:
	docker build data/. -t worshipdata
	docker build . -t worship

dockerrun:
	# docker run \
	# 	-d \
	# 	--volumes-from worshipdata \
	# 	--restart always \
	# 	-p 9000:8080 \
	# 	-p 8888:8888 \
	# 	worship

dockerupload:
	echo "Assumes your Docker username is ericmjl! Hit Ctrl+C if this isn't true."
	docker login
	docker tag worship ericmjl/worship
	docker push ericmjl/worship

start: dockerbuild dockerrun

push: dockerbuild dockerupload

test:
	py.test --cov --cov-report term-missing
