"""Optional utilities to run commands inside a Docker container."""

import tempfile
from pathlib import Path
from typing import List

try:
    import docker
except Exception:  # docker might not be installed
    docker = None


def run_in_container(image: str, command: List[str], volume: Path) -> str:
    if docker is None:
        raise RuntimeError("docker SDK not available")
    client = docker.from_env()
    container = client.containers.run(
        image,
        command,
        volumes={str(volume): {"bind": "/workspace", "mode": "rw"}},
        working_dir="/workspace",
        detach=True,
        mem_limit="512m",
        cpu_period=100000,
        cpu_quota=50000,
    )
    result = container.logs(stream=False).decode()
    container.remove(force=True)
    return result
