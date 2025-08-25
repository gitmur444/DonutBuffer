from pathlib import Path

from src.core.env import EnvManager
from .check_dependencies import run_dependencies_check
from .check_github import run_github_access_check
from .check_mcp import run_mcp_config_check
from .check_ambient import run_ambient_e2e_check


def run_preflight(donut_dir: Path) -> tuple[bool, list[str]]:
    env = EnvManager(donut_dir)
    env.load_env_file()

    statuses: list[str] = []
    ok_all = True

    ok, msg = run_dependencies_check(donut_dir)
    statuses.append(msg)
    ok_all = ok_all and ok

    ok, msg = run_github_access_check(env)
    statuses.append(msg)
    ok_all = ok_all and ok

    ok, msg = run_mcp_config_check(donut_dir)
    statuses.append(msg)
    ok_all = ok_all and ok

    ok, msg = run_ambient_e2e_check(donut_dir)
    statuses.append(msg)
    ok_all = ok_all and ok

    return ok_all, statuses


