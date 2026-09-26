"""Core modules for tool-ghcr-docker-packager."""
from .models import ContainerSpec, TargetRegistry, MultiArchPlatform
from .docker_builder import DockerBuilder, BuildxCommand
from .cosign_signer import CosignSigner, SignaturePlan
from .workflow_generator import GhcrWorkflowGenerator

__all__ = [
    "ContainerSpec",
    "TargetRegistry",
    "MultiArchPlatform",
    "DockerBuilder",
    "BuildxCommand",
    "CosignSigner",
    "SignaturePlan",
    "GhcrWorkflowGenerator",
]
