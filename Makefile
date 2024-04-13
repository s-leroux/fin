.PHONY: tests tests-all examples compile

compile:
	python3 setup.py build_ext --inplace

tests: compile
	python3 -m unittest discover -s tests -t .

examples: compile
	for f in $$(find examples -name "*.py"); do \
	  echo "$$f" >&2; \
	  PYTHONPATH="$$PWD" python3 "$$f" > /dev/null || exit 1; \
	done

snippets: compile
	mkdir -p docs/snippets/_output
	set -e; \
	export FIN_GNUPLOT="tail -2"; \
	dir=docs/snippets/; \
	for f in "$${dir}"snippet_*_001.py; do \
	  echo "$${f}"; \
	  f="$${f##*/}"; \
	  stem="$${f%_001.py}"; \
	  cat "$${dir}$${stem}"_*.py | python3 > "$${dir}"_output/"$${stem}".txt; \
	  sed -i 's/ at 0x[0-9a-f]*//' "$${dir}"_output/"$${stem}".txt; \
	  diff "$${dir}"_output/"$${stem}".txt "$${dir}"_expected/"$${stem}".txt; \
	done

tests-all: compile
	SLOW_TESTS=yes python3 -m unittest discover -s tests -t .
	$(MAKE) snippets
	$(MAKE) examples
	@echo OK
