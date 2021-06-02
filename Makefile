help:
	@echo "clean - get rid of build artifacts & metadata"
	@echo "test - execute tests"
	@echo "dist - build a distribution; calls test, clean-build and clean-pyc"
	@echo "check - check the quality of the built distribution; calls dist for you"
	@echo "release - register and upload to PyPI"

clean: clean-pyc
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

test: clean-pyc
	python3.9 runtests.py

dist: test clean clean-pyc
	python3.9 setup.py sdist bdist_wheel

release:
	@echo "INSTRUCTIONS:"
	@echo "- pip install wheel twine"
	@echo "- python3.9 setup.py sdist bdist_wheel"
	@echo "- ls dist/"
	@echo "- twine register dist/???"
	@echo "- twine upload dist/*"
