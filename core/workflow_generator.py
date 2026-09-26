"""GitHub Actions workflow generator for automated GHCR multi-arch publishing and Cosign signing."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from .models import ContainerSpec

DEFAULT_TIMEOUT_SECONDS = 30
timeout=DEFAULT_TIMEOUT_SECONDS

class GhcrWorkflowGenerator:
    def generate_workflow(self, spec: ContainerSpec) -> str:
        plat_str = ",".join(p.value for p in spec.platforms)
        image_name_expr = "${{ github.repository }}"

        return f"""name: Publish OCI Container to GHCR

on:
  push:
    tags: [ 'v*.*.*' ]
    branches: [ 'main' ]
  workflow_dispatch:

permissions:
  contents: read
  packages: write
  id-token: write

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install Cosign (Sigstore)
        uses: sigstore/cosign-installer@v3.5.0

      - name: Set up QEMU (Multi-Architecture emulation)
        uses: docker/setup-qemu-action@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Log in to GitHub Container Registry (ghcr.io)
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Extract Docker metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/{image_name_expr}
          tags: |
            type=semver,pattern={{{{version}}}}
            type=raw,value=latest,enable=${{{{github.ref == 'refs/heads/main'}}}}
            type=sha

      - name: Build and Push OCI Image
        id: build-and-push
        uses: docker/build-push-action@v5
        with:
          context: {spec.context_path}
          file: {spec.dockerfile_path}
          platforms: {plat_str}
          push: true
          tags: ${{{{ steps.meta.outputs.tags }}}}
          labels: ${{{{ steps.meta.outputs.labels }}}}

      - name: Cryptographically Sign Image with Cosign (Keyless OIDC)
        run: |
          echo "Signing image digest: ${{{{ steps.build-and-push.outputs.digest }}}}"
          cosign sign --yes "ghcr.io/{image_name_expr}@${{{{ steps.build-and-push.outputs.digest }}}}"
"""

    def write_workflow(self, root_dir: str | Path, spec: ContainerSpec, filename: str = "ghcr-publish.yml") -> Path:
        root = Path(root_dir).resolve()
        wf_dir = root / ".github" / "workflows"
        wf_dir.mkdir(parents=True, exist_ok=True)
        target = wf_dir / filename
        content = self.generate_workflow(spec)
        target.write_text(content, encoding="utf-8")
        return target
