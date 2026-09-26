"""Hermetic offline unit tests for tool-ghcr-docker-packager."""
import tempfile
import unittest
from pathlib import Path

from core.models import ContainerSpec, MultiArchPlatform, TargetRegistry
from core.docker_builder import DockerBuilder
from core.cosign_signer import CosignSigner
from core.workflow_generator import GhcrWorkflowGenerator

DEFAULT_TIMEOUT_SECONDS = 30
timeout=DEFAULT_TIMEOUT_SECONDS

class TestGhcrPackagerOffline(unittest.TestCase):
    def test_01_container_spec_image_refs(self):
        spec = ContainerSpec(
            owner="MyOrg",
            image_name="FastService",
            tags=["v1.0.0", "latest"]
        )
        self.assertEqual(spec.get_primary_image_ref(), "ghcr.io/myorg/fastservice:v1.0.0")
        all_refs = spec.get_all_image_refs()
        self.assertEqual(len(all_refs), 2)
        self.assertIn("ghcr.io/myorg/fastservice:latest", all_refs)

    def test_02_docker_builder_synthesizes_buildx_command(self):
        spec = ContainerSpec(
            owner="Alice",
            image_name="WebGate",
            tags=["v2.0.0"],
            platforms=[MultiArchPlatform.LINUX_AMD64, MultiArchPlatform.LINUX_ARM64]
        )
        builder = DockerBuilder()
        cmd = builder.synthesize_command(spec)

        self.assertIn("docker buildx build", cmd.raw_command)
        self.assertIn("--platform linux/amd64,linux/arm64", cmd.raw_command)
        self.assertIn("-t ghcr.io/alice/webgate:v2.0.0", cmd.raw_command)
        self.assertIn("--push", cmd.raw_command)

    def test_03_cosign_signer_plan(self):
        signer = CosignSigner()
        plan = signer.plan_signature("ghcr.io/org/app:v1.0.0", sbom_path="sbom.spdx.json")
        self.assertIn("cosign sign --yes ghcr.io/org/app:v1.0.0", plan.sign_command)
        self.assertIn("cosign attest --yes --predicate sbom.spdx.json", plan.attest_command)

    def test_04_workflow_generator_contains_oidc_and_cosign(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            spec = ContainerSpec(owner="my-team", image_name="ai-kernel")
            gen = GhcrWorkflowGenerator()
            wf_file = gen.write_workflow(tmp, spec)

            self.assertTrue(wf_file.is_file())
            content = wf_file.read_text(encoding="utf-8")

            # Check permissions
            self.assertIn("id-token: write", content)
            self.assertIn("packages: write", content)
            # Check cosign
            self.assertIn("sigstore/cosign-installer", content)
            # Check buildx
            self.assertIn("docker/setup-buildx-action", content)
            # Check concurrency
            self.assertIn("concurrency:", content)

    def test_05_dockerfile_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            df = tmp / "Dockerfile"
            df.write_text("FROM python:3.12-slim\nCMD ['python']\n", encoding="utf-8")

            builder = DockerBuilder()
            self.assertTrue(builder.validate_dockerfile(df))

            bad_df = tmp / "Empty.txt"
            bad_df.write_text("hello world\n", encoding="utf-8")
            self.assertFalse(builder.validate_dockerfile(bad_df))

    def test_06_workflow_generator_with_cache_and_trivy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            spec = ContainerSpec(owner="my-team", image_name="ai-kernel", enable_cache=True, enable_trivy=True)
            gen = GhcrWorkflowGenerator()
            wf_file = gen.write_workflow(tmp, spec)

            content = wf_file.read_text(encoding="utf-8")
            self.assertIn("cache-from: type=gha", content)
            self.assertIn("cache-to: type=gha,mode=max", content)
            self.assertIn("aquasecurity/trivy-action", content)
            self.assertIn("Run Trivy Security Vulnerability Scan", content)

if __name__ == "__main__":
    unittest.main()
