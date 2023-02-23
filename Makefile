.PHONY: tests

tests:
	python3 -m unittest discover -s tests -t .

tests-all:
	SLOW_TESTS=yes python3 -m unittest discover -s tests -t .
