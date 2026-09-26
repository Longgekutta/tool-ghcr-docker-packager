"""Docker Buildx multi-arch command generator and local execution engine."""
from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import List, Optional
from .models import ContainerSpec

DEFAULT_TIMEOUT_SECONDS = 30
timeout=DEFAULT_TIMEOUT_SECONDS

@dataclass
class BuildxCommand:
    raw_command: str
    args: List[str]
    target_image_refs: List[str]
    platforms: List[str]

class DockerBuilder:
    def synthesize_command(self, spec: ContainerSpec) -> BuildxCommand:
        args = ["docker", "buildx", "build"]

        # Platforms
        plat_str = ",".join(p.value for p in spec.platforms)
        args.extend(["--platform", plat_str])

        # Dockerfile & Context
        args.extend(["-f", spec.dockerfile_path])

        # Tags
        refs = spec.get_all_image_refs()
        for ref in refs:
            args.extend(["-t", ref])

        # Push flag
        if spec.enable_push:
            args.append("--push")

        args.append(spec.context_path)

        return BuildxCommand(
            raw_command=" ".join(args),
            args=args,
            target_image_refs=refs,
            platforms=[p.value for p in spec.platforms]
        )

    def validate_dockerfile(self, dockerfile_path: str | Path) -> bool:
        path = Path(dockerfile_path).resolve()
        if not path.is_file():
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return "FROM " in content
        except Exception:
            return False
