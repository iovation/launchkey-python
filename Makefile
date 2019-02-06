ci-py27: ci-py2

ci-pypy: ci-py2

ci-py34: ci

ci-py35: ci

ci-py36: ci

ci-py37: ci

ci-py38: tests-py3

ci-pypy3: ci



ci: dependencies-py3 tests-py3 flake8-py3 pylint-py3

ci-py2: tests-py2 flake8-py2 pylint-py2

dependencies-py3:
		pip install -r test_requirements.txt

dependencies-py2:
		pip install -r test_requirements_py2.txt

test:
		coverage run --source="launchkey" setup.py nosetests
		coverage report --fail-under=100

tests-py2: dependencies-py2 test integration

tests-py3: dependencies-py3 test integration

flake8:
		flake8 launchkey

flake8-py2: dependencies-py2 flake8

flake8-py3: dependencies-py3 flake8

pylint:
		pylint launchkey

pylint-py2: dependencies-py2 pylint

pylint-py3: dependencies-py3 pylint

integration:
		behave
