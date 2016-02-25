
## Schema.org Course Extension Makefile

default: test

PYTHON=$(shell which python)
test:
	$(PYTHON) _build.py

test-all:
	$(MAKE) test
	$(MAKE) test-schemaorg

test-schemaorg:
	$(MAKE) -C ../../../ test

build:
	$(MAKE) build-course-rdfa

install:
	$(MAKE) -C ../../../ install_requirements_tests # install_pip

build-course-rdfa:
	@# pip install -r ../../../requirements-test.txt ( rdflib )
	$(MAKE) build-course-rdfa-jsonld

build-course-rdfa-jsonld:
	rdfpipe -i rdfa1.1 -o json-ld ./course.rdfa.html5.html \
		| tee ./course.rdfa.html5.html.jsonld
