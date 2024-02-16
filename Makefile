.PHONY: tests tests-all examples compile

compile:
	python3 setup.py build_ext --inplace

tests: compile
	python3 -m unittest discover -s tests -t .

examples: compile
	for f in $$(find examples -name "*.py"); do \
	  echo "$$f"; \
	  PYTHONPATH="$$PWD" python3 "$$f" || exit 1; \
	done

tests-all: compile
	SLOW_TESTS=yes python3 -m unittest discover -s tests -t .
	$(MAKE) examples
	@echo OK
