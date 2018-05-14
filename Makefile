init:
	pip install pipenv --upgrade
	pipenv install --dev --ignore-pipfile

test:
	pipenv run python -m unittest discover

lint:
	-pipenv run pylint api db
