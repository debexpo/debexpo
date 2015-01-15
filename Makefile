help:
	@echo "make targets:"
	@echo "    build: build debexpo"
	@echo "    install: install debexpo"
	@echo "    test: test debexpo"

build:
	python setup.py build
	(cd docs && make html)
	python setup.py compile_catalog
	python setup.py sdist
	#paster make-config debexpo debexpo.ini

install:
	python setup.py install

test:
	nosetests --with-pylons=test.ini

clean:
	python setup.py clean

.PHONY: help build install test
