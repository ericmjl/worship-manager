test:
	py.test --cov --cov-report term-missing -v

run:
	python run.py

sync:
	bash sync.sh
