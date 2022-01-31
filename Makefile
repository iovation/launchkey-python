ci-py36: ci

ci-py37: test

ci-py38: test

ci-py39: test

ci-pypy3: test

ci: dependencies coverage flake8 pylint deps-check

test:
		python setup.py test

dependencies:
		pip install --upgrade pipenv
		pipenv install --three --dev --ignore-pipfile

coverage:
		pipenv run coverage run --source="launchkey" setup.py nosetests
		pipenv run coverage report --fail-under=100

flake8:
		pipenv run flake8 launchkey

pylint:
		pipenv run pylint launchkey

deps-check:
		pipenv check