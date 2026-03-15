from importlib import import_module
from pathlib import Path

TESTS = {}

tests_dir = Path(__file__).resolve().parent

for item in tests_dir.iterdir():
    if not item.is_dir():
        continue

    if item.name.startswith("__"):
        continue

    test_def_file = item / "test_def.py"
    if not test_def_file.exists():
        continue

    module_name = f"tests.{item.name}.test_def"
    module = import_module(module_name)

    if not hasattr(module, "TEST_DEF"):
        continue

    test_def = module.TEST_DEF
    test_key = test_def["key"]
    TESTS[test_key] = test_def
