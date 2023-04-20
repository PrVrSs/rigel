SHELL := /usr/bin/env bash


.PHONY: unit
unit:
	poetry run pytest

.PHONY: mypy
mypy:
	poetry run mypy rigel

.PHONY: lint
lint:
	poetry run pylint rigel


.PHONY: test
test: lint unit
