.PHONY: tests

tests:
	python3 -m unittest discover -s tests -t .

tests-all:
	LONG_TESTS=yes python3 -m unittest discover -s tests -t .
