#!/usr/bin/env bash

set -e

poetry install --without dev --no-ansi --no-root

exec poetry run python -m weather-tracker.manage runserver