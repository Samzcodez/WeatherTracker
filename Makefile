.PHONY: install
install:
	poetry install

.PHONY: run-server
run-server:
	poetry run python -m weather-tracker.manage runserver
