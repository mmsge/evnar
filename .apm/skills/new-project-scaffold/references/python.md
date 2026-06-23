# Python Reference

## Toolchain

| Concern | Tool |
|---|---|
| Python version | 3.12+ |
| Package manager | uv (preferred) or pip + venv |
| Linter | Ruff |
| Formatter | Ruff format |
| Type checking | mypy |
| Test runner | pytest |
| Coverage | pytest-cov |

---

## `pyproject.toml` template

```toml
[project]
name = "<project-name>"
version = "0.1.0"
description = "<description>"
requires-python = ">=3.12"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "mypy>=1.10",
    "ruff>=0.4",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
ignore = []

[tool.mypy]
python_version = "3.12"
strict = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing --cov-report=lcov --cov-fail-under=80"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
exclude_lines = ["pragma: no cover", "if TYPE_CHECKING:"]
```

## Project layout

```
<project-name>/
├── src/
│   └── <package>/
│       ├── __init__.py
│       └── core.py
├── tests/
│   ├── __init__.py
│   └── test_core.py
├── pyproject.toml
├── README.md
└── .gitignore
```

## Test file pattern

```python
# tests/test_core.py
import pytest
from <package>.core import my_function


class TestMyFunction:
    def test_valid_input(self):
        assert my_function("hello") == "HELLO"

    def test_empty_string(self):
        assert my_function("") == ""

    def test_invalid_type_raises(self):
        with pytest.raises(TypeError, match="Expected str"):
            my_function(123)  # type: ignore

    @pytest.mark.parametrize("value,expected", [
        ("foo", "FOO"),
        ("Bar", "BAR"),
    ])
    def test_parametrized(self, value: str, expected: str):
        assert my_function(value) == expected
```

## GitHub Actions — CI

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: astral-sh/setup-uv@v4
        with:
          version: "latest"

      - name: Set up Python
        run: uv python install 3.12

      - name: Install dependencies
        run: uv sync --extra dev

      - name: Lint
        run: uv run ruff check .

      - name: Format check
        run: uv run ruff format --check .

      - name: Type check
        run: uv run mypy src

      - name: Test
        run: uv run pytest

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: coverage.lcov
```

## `.gitignore`

```
__pycache__/
*.pyc
*.pyo
.venv/
venv/
.uv/
dist/
build/
*.egg-info/
.coverage
coverage.lcov
htmlcov/
.mypy_cache/
.ruff_cache/
.env
```
