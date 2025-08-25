from pathlib import Path

from src.setup.mcp_setup import MCPSetup


def run_mcp_config_check(donut_dir: Path) -> tuple[bool, str]:
    setup = MCPSetup(donut_dir)
    # Явно печатаем шаг 3
    setup.print_step(3, "Настройка GitHub MCP Server")
    ok = setup.create_mcp_config()
    return ok, "mcp: ok" if ok else "mcp: fail"


