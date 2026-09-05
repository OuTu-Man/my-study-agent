fmt:
	uv run black -l 120 . && ruff check . --fix && ruff format .
