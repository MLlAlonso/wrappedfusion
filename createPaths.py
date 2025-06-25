from pathlib import Path

paths = [
    "app/__init__.py",
    "app/config/__init__.py",
    "app/database/__init__.py",
    "app/database/models/__init__.py",
    "app/api/__init__.py",
    "app/api/v1/__init__.py",
    "app/api/v1/endpoints/__init__.py",
    "app/business/__init__.py",
    "app/business/services/__init__.py",
    "app/tests/__init__.py",
    "app/tests/unit/__init__.py",
    "app/tests/integration/__init__.py"
]

for path in paths:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).touch()