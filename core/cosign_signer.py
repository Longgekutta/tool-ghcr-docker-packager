"""Cosign / Sigstore container image signing and attestation planner."""
from dataclasses import dataclass
from typing import List, Optional

DEFAULT_TIMEOUT_SECONDS = 30
timeout=DEFAULT_TIMEOUT_SECONDS

@dataclass
class SignaturePlan:
    image_ref: str
    sign_command: str
    attest_command: Optional[str]
    verify_command: str

class CosignSigner:
    def plan_signature(self, image_ref: str, sbom_path: Optional[str] = None) -> SignaturePlan:
        sign_cmd = f"cosign sign --yes {image_ref}"
        attest_cmd = None
        if sbom_path:
            attest_cmd = f"cosign attest --yes --predicate {sbom_path} --type spdx {image_ref}"
        verify_cmd = f"cosign verify {image_ref} --certificate-identity-regexp 'https://github.com/'"

        return SignaturePlan(
            image_ref=image_ref,
            sign_command=sign_cmd,
            attest_command=attest_cmd,
            verify_command=verify_cmd
        )
