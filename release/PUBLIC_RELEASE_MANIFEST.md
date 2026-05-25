# AXON OS Public Release Manifest

This file defines what is intended for the AXON OS Developer Preview public release.

## Public Release Channel

AXON OS Developer Preview 0.1

## Safe To Publish

The following areas are intended for public preview:

- axon command wrapper
- cli/
- environment/
- release/
- reports/
- installation/
- approvals/
- operations/
- execution/
- execution_control/
- action_control/
- action_executor/
- workflows/
- workspace/
- data_sources/
- orchestrator/
- docs/DEVELOPER_PREVIEW.md
- docs/VM_GPU_GUIDE.md
- README.md
- SECURITY.md
- NOTICE.md
- LICENSE
- VERSION
- .gitignore

## Must Not Be Published

The following must not be included in a public release:

- .venv/
- backups/
- __pycache__/
- *.pyc
- environment/runtime_reports/
- jupyter-env/
- models/
- ai-container/models/
- logs
- .env
- kaggle.json
- secrets
- tokens
- private credentials
- large model files

## GPU Policy

GPU drivers, ROCm, NVIDIA drivers, and bitsandbytes are not automatically installed in this Developer Preview.

AXON uses VM-safe CPU mode when running inside VMware or similar environments without confirmed GPU passthrough.

## Release Note

This is not a final OS release. It is a Developer Preview focused on runtime checks, safety, reports, VM/GPU awareness, and CLI-based preview operation.

Developed by Abdullah Ali.
