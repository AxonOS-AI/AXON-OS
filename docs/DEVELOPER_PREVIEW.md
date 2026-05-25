# AXON OS Developer Preview 0.1

AXON OS is an AI-native operating layer focused on safe AI workflow orchestration, runtime checks, VM/GPU awareness, approval-based operation planning, and developer reports.

This is not a final operating system release. It is an early Developer Preview.

## What Works Now

- AXON CLI command wrapper
- AXON boot screen
- AXON Doctor health check
- Runtime package verification
- Virtualization detection
- GPU capability detection
- Acceleration policy
- VM-safe CPU mode
- Safe installation planning
- Approval-based operation planning
- Execution reports
- Markdown final reports

## Available Commands

- axon start
- axon start --fast
- axon doctor
- axon version
- axon help

## Safety Model

AXON Developer Preview does not automatically install GPU drivers, NVIDIA drivers, ROCm, bitsandbytes, or system-level packages.

AXON does not use --break-system-packages.

Operations that can modify the system must require explicit approval.

## VM and GPU Policy

If AXON runs inside VMware or a similar virtual machine without confirmed real GPU passthrough, AXON uses VM-safe CPU mode.

For Windows users who need GPU acceleration, AXON should recommend WSL2 mode when supported.

For advanced users, bare metal Linux or Proxmox, ESXi, or KVM GPU passthrough may be used.

## Deferred Capabilities

- Full GPU driver automation
- bitsandbytes installation
- ROCm setup
- Real dataset download workflow
- Training workflow execution
- ISO image release

## Readiness Report

The preview readiness report is available at release/AXON_PREVIEW_READINESS_REPORT.md.

## Credit

Developed by Abdullah Ali.
