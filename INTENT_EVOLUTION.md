# INTENT EVOLUTION: tool-ghcr-docker-packager

## Initial State
- Manual single-arch docker builds fail on ARM cloud instances, lack provenance signing, and require complex registry auth setups.

## Transduced Invariants
1. Automated QEMU + Buildx multi-arch build pipelines (amd64 / arm64).
2. Direct publishing to GitHub Container Registry (`ghcr.io`).
3. Keyless Sigstore/Cosign cryptographic container signing.
4. Automatic generation of zero-maintenance GitHub Actions publishing workflows.
