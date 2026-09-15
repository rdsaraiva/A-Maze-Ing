all: run

clean:
	rm -rf __pycache__ .mypy_cache .pytest_cache
	rm -rf build dist mazegen.egg-info

lint:
	python3 -m flake8 .
	python3 -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	python3 -m flake8 .
	python3 -m mypy . --strict

run: config.txt a_maze_ing.py
	@python3 a_maze_ing.py config.txt

debug: config.txt a_maze_ing.py
	python3 -m pdb a_maze_ing.py config.txt

install: requirements.txt
	python3 -m pip install -r requirements.txt

build:
	python3 -m venv venv
	python3 -m build --outdir .
.PHONY: all clean lint run lint-strict debug install build
