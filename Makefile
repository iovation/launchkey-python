ci-py27: ci

ci-pypy: ci

ci-py34: ci

ci-py35: ci

ci-py36: ci

ci-pypy3: ci

ci-py37: tests  # flake8 and pylint need patches to work with python 3.7



ci: tests flake8 pylint

dependencies:
		pip install -r test_requirements.txt

tests: dependencies
		coverage run --source="launchkey" setup.py nosetests
		coverage report --fail-under=100

flake8: dependencies
		flake8 launchkey

pylint: dependencies
		pylint launchkey
