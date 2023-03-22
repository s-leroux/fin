.PHONY: tests examples

tests:
	python3 -m unittest discover -s tests -t .

examples:
	for f in $$(find examples -name "*.py"); do \
	  echo "$$f"; \
	  PYTHONPATH="$$PWD" python3 "$$f" > /dev/null || exit 1; \
	done

tests-all:
	SLOW_TESTS=yes python3 -m unittest discover -s tests -t .
	$(MAKE) examples
	@echo OK
