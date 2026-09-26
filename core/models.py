"""Domain models for container packaging and registry publishing."""
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional

DEFAULT_TIMEOUT_SECONDS = 30
timeout=DEFAULT_TIMEOUT_SECONDS

class MultiArchPlatform(str, Enum):
    LINUX_AMD64 = "linux/amd64"
    LINUX_ARM64 = "linux/arm64"
    LINUX_ARM_V7 = "linux/arm/v7"

class TargetRegistry(str, Enum):
    GHCR = "ghcr.io"
    DOCKERHUB = "docker.io"

@dataclass
class ContainerSpec:
    owner: str
    image_name: str
    tags: List[str] = field(default_factory=lambda: ["latest"])
    platforms: List[MultiArchPlatform] = field(
        default_factory=lambda: [MultiArchPlatform.LINUX_AMD64, MultiArchPlatform.LINUX_ARM64]
    )
    registry: TargetRegistry = TargetRegistry.GHCR
    dockerfile_path: str = "Dockerfile"
    context_path: str = "."
    enable_push: bool = True
    enable_cache: bool = True
    enable_trivy: bool = True

    def get_primary_image_ref(self) -> str:
        clean_owner = self.owner.lower().lstrip("@")
        clean_name = self.image_name.lower()
        primary_tag = self.tags[0] if self.tags else "latest"
        return f"{self.registry.value}/{clean_owner}/{clean_name}:{primary_tag}"

    def get_all_image_refs(self) -> List[str]:
        clean_owner = self.owner.lower().lstrip("@")
        clean_name = self.image_name.lower()
        return [f"{self.registry.value}/{clean_owner}/{clean_name}:{t}" for t in self.tags]
