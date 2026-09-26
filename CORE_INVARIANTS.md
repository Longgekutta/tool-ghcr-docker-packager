# CORE INVARIANTS: tool-ghcr-docker-packager

1. Multi-Arch Compliance Invariance:
   - Generated Docker Buildx configurations MUST target both `linux/amd64` and `linux/arm64` by default.

2. Cryptographic Attestation Invariance:
   - Workflows MUST enforce OIDC permissions (`id-token: write`, `packages: write`) for keyless Sigstore/Cosign provenance signing.

3. Offline Simulation Invariance:
   - CLI command synthesis, Dockerfile linting, and workflow generation execute 100% offline without Docker daemon or network queries.
