#!/usr/bin/env python3
"""Static checks for the CI/CD release contract."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text()


errors: list[str] = []


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        errors.append(f"missing {label}: {needle}")


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        errors.append(f"unexpected {label}: {needle}")


def job_block(text: str, job_name: str) -> str:
    pattern = re.compile(rf"^  {re.escape(job_name)}:\n", re.MULTILINE)
    match = pattern.search(text)
    if not match:
        errors.append(f"missing job block: {job_name}")
        return ""

    next_match = re.compile(r"^  [a-z0-9][a-z0-9_-]*:\n", re.MULTILINE).search(
        text, match.end()
    )
    end = next_match.start() if next_match else len(text)
    return text[match.start() : end]


deploy = read(".github/workflows/deploy.yml")
build_backend = read(".github/workflows/_build-backend-image.yml")
deploy_backend = read(".github/workflows/_deploy-backend.yml")
promote_backend = read(".github/workflows/promote-backend.yml")
promote_backend_job = job_block(deploy, "promote-backend-production")

require(
    deploy,
    "uses: ./.github/workflows/_build-backend-image.yml",
    "dev backend build workflow call",
)
require(
    deploy,
    "needs: [ci, changes, build-backend-image]",
    "backend deploy dependency on build output",
)
require(
    deploy,
    "github.ref == 'refs/heads/develop'",
    "develop-only backend auto deploy guard",
)
require(
    deploy,
    "image: ${{ needs.build-backend-image.outputs.image }}",
    "backend deploy using build output image",
)
require(
    deploy,
    "uses: ./.github/workflows/promote-backend.yml",
    "production backend promotion workflow call",
)
require(
    deploy,
    "github.ref == 'refs/heads/production'",
    "production backend auto promotion guard",
)
require(
    deploy,
    "promote-backend-production:",
    "named production backend promotion job",
)
require(
    promote_backend_job,
    "if: github.ref == 'refs/heads/production'",
    "unconditional production backend promotion override",
)
forbid(
    promote_backend_job,
    "needs.changes.outputs.backend",
    "production backend promotion gated on post-fast-forward path detection",
)

require(
    build_backend,
    "aha-coms-sicu-backend",
    "stable backend image repository name",
)
require(
    build_backend,
    'IMAGE_REF="${{ steps.repo.outputs.image_repository }}@$IMAGE_DIGEST"',
    "immutable image output",
)

require(
    deploy_backend,
    "image:",
    "deploy-existing-image input",
)
require(
    deploy_backend,
    'docker pull "${{ inputs.image }}"',
    "deploy image pull",
)
require(
    deploy_backend,
    'docker run --rm --network host \\',
    "migrations running from deployed image",
)
require(
    deploy_backend,
    'image: ${{ inputs.image }}',
    "Cloud Run deploy by existing image",
)
require(
    deploy_backend,
    "tests/backend-health.spec.ts tests/auth-enforcement.spec.ts",
    "selected backend smoke tests",
)
require(
    deploy_backend,
    "Upload verified backend release manifest",
    "verified release artifact upload",
)
require(
    deploy_backend,
    "### Verified backend release",
    "dev deploy promotion guidance",
)
forbid(
    deploy_backend,
    "docker/build-push-action@",
    "inline backend image build in deploy workflow",
)

require(
    promote_backend,
    "workflow_dispatch:",
    "manual promotion entrypoint",
)
require(
    promote_backend,
    "workflow_call:",
    "reusable promotion entrypoint",
)
require(
    promote_backend,
    "environment: production",
    "production promotion target",
)
require(
    promote_backend,
    "release_sha:",
    "promotion release sha input",
)
require(
    promote_backend,
    "backend-release-manifest",
    "verified release manifest artifact handling",
)
require(
    promote_backend,
    "actions/artifacts/${artifact_id}/zip",
    "artifact zip download path",
)
require(
    promote_backend,
    "git merge-base --is-ancestor",
    "production ancestry-based release resolution",
)
require(
    promote_backend,
    'if [ "$REF_NAME" = "production" ]; then',
    "production fast-forward auto-resolution gate",
)
require(
    promote_backend,
    "Provide either release_sha or image, or run this workflow from the production branch after fast-forwarding it to develop",
    "fast-forward promotion guidance",
)
forbid(
    promote_backend,
    "gh run download \"$RUN_ID\" --name backend-release-manifest",
    "legacy artifact download implementation",
)
forbid(
    promote_backend,
    "after merging develop",
    "stale merge-based release guidance",
)
require(
    promote_backend,
    "emit_verified_release",
    "shared verified release summary helper",
)
require(
    promote_backend,
    "image: ${{ needs.resolve-release.outputs.image }}",
    "resolved promotion image wiring",
)

if errors:
    print("Release contract check failed:")
    for error in errors:
        print(f"- {error}")
    raise SystemExit(1)

print("Release contract check passed.")
