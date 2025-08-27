from pathlib import Path
from typing import Callable, Optional

from src.core.env_manager import EnvManager
from .check_dependencies import run_dependencies_check
from .check_github import run_github_access_check
from .check_mcp import run_mcp_config_check
from .check_ambient import run_ambient_e2e_check
from .test_integration import IntegrationTest


def run_preflight(donut_dir: Path, on_progress: Optional[Callable[[str], None]] = None) -> tuple[bool, list[str]]:
    env = EnvManager(donut_dir)
    env.load_env_file()

    statuses: list[str] = []
    ok_all = True

    ok, msg = run_dependencies_check(donut_dir)
    statuses.append(msg)
    if on_progress:
        try:
            on_progress(msg)
        except Exception:
            pass
    ok_all = ok_all and ok

    ok, msg = run_github_access_check(env)
    statuses.append(msg)
    if on_progress:
        try:
            on_progress(msg)
        except Exception:
            pass
    ok_all = ok_all and ok

    ok, msg = run_mcp_config_check(donut_dir)
    statuses.append(msg)
    if on_progress:
        try:
            on_progress(msg)
        except Exception:
            pass
    ok_all = ok_all and ok

    # Шаг 4: Интеграционные проверки (GitHub API + cursor-agent)
    integration = IntegrationTest(env)
    ok = integration.test_integration()
    msg = "integration: ok" if ok else "integration: fail"
    statuses.append(msg)
    if on_progress:
        try:
            on_progress(msg)
        except Exception:
            pass
    ok_all = ok_all and ok

    ok, msg = run_ambient_e2e_check(donut_dir)
    statuses.append(msg)
    if on_progress:
        try:
            on_progress(msg)
        except Exception:
            pass
    ok_all = ok_all and ok

    return ok_all, statuses


