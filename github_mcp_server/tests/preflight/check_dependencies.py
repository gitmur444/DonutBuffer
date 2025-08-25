from pathlib import Path

from src.core.dependency_checker import DependencyChecker
from src.core.env_manager import EnvManager


def run_dependencies_check(donut_dir: Path) -> tuple[bool, str]:
    env = EnvManager(donut_dir)
    env.load_env_file()
    checker = DependencyChecker()
    ok = checker.check_dependencies()
    return ok, "dependencies: ok" if ok else "dependencies: fail"


