VENV_DIR := ".venv"

requirements.txt: requirements.in
	pip-compile --output-file $@ --quiet $<

venv: requirements.txt
	python3 -m venv ${VENV_DIR}
	${VENV_DIR}/bin/python -m pip install --requirement $< --no-deps
	${VENV_DIR}/bin/python -m pip freeze > $@

.PHONY: test
test:
	${VENV_DIR}/bin/python -m pytest tests 