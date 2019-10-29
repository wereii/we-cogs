## Kindly borrowed from https://github.com/Cog-Creators/Red-DiscordBot/blob/V3/develop/Makefile
PYTHON ?= python3.7

# Python Code Style
reformat:
	$(PYTHON) -m black -l 99 --target-version py37 `git ls-files "*.py"`
stylecheck:
	$(PYTHON) -m black --check -l 99 --target-version py37 `git ls-files "*.py"`
