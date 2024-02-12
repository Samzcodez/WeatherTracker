.PHONY: install
install:
	poetry install

.PHONY: migrate
migrate:
	poetry run python -m weather-tracker.manage migrate

.PHONY: run-server
run-server:
	poetry run python -m weather-tracker.manage runserver
