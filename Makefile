init:
	pip install pipenv --upgrade
	pipenv install --dev --skip-lock

test:
	pipenv run python -m unittest discover

lint:
	pipenv run pylint api db
