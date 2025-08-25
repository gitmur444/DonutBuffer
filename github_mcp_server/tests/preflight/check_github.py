from src.core.env import EnvManager
from src.setup.github_setup import GitHubSetup


def run_github_access_check(env_manager: EnvManager) -> tuple[bool, str]:
    setup = GitHubSetup(env_manager)
    # Явно печатаем шаг 2, без интерактива (только валидация)
    setup.print_step(2, "Настройка GitHub токена")
    token = env_manager.get_env_var("GITHUB_TOKEN")
    if not token:
        setup.print_error("GITHUB_TOKEN не установлен")
        return False, "github: no token"
    ok = setup.validate_token(token)
    return ok, "github: ok" if ok else "github: fail"


