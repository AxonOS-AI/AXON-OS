# AXON OS

AI-Native Operating Layer built on Ubuntu.

Developed by Abdullah Ali.

## Developer Preview 0.1

AXON OS is currently available as a Developer Preview.

This is not a final operating system release. It is an early technical preview focused on safe runtime checks, VM/GPU awareness, approval-based operation planning, CLI-based startup, and developer-facing reports.

## What AXON Does

AXON OS is an intelligent execution layer designed to transform traditional Linux systems into AI-native environments.

Instead of launching tools manually, AXON focuses on understanding user intent and orchestrating intelligent workflows locally.

## Quick Start

Clone or open the project directory:

    cd ~/AxonOS

Run setup:

    ./setup_axon.sh

Start AXON:

    axon start

Or use fast startup mode:

    axon start --fast

Run environment health check:

    axon doctor

Show version:

    axon version

## Available Commands

- axon start
- axon start --fast
- axon doctor
- axon version
- axon help

## Current Preview Features

- AXON CLI command wrapper
- AXON boot screen
- AXON Doctor environment health check
- Runtime package verification
- Virtualization detection
- GPU capability detection
- Acceleration policy
- VM-safe CPU mode
- Safe installation planning
- Approval-based operation planning
- Execution reports
- Markdown final reports

## VM and GPU Policy

AXON does not automatically install GPU drivers, NVIDIA drivers, ROCm, or bitsandbytes.

If AXON runs inside VMware or a similar virtual machine without confirmed real GPU passthrough, AXON uses VM-safe CPU mode.

For Windows users who need GPU acceleration, AXON should recommend WSL2 mode when supported.

For advanced users, bare metal Linux or Proxmox, ESXi, or KVM GPU passthrough may be used.

## Requirements

Minimal Developer Preview setup uses:

- Python 3
- python3-venv
- Ubuntu or Ubuntu-based Linux environment

Optional AI packages are listed in requirements-ai.txt.

Optional GPU packages are listed in requirements-gpu.txt and must not be installed blindly.

## Safety Model

AXON Developer Preview follows these safety rules:

- No automatic GPU driver installation
- No automatic ROCm installation
- No automatic NVIDIA driver installation
- No automatic bitsandbytes installation
- No system Python modification
- No use of --break-system-packages
- Runtime packages are isolated in the AXON virtual environment
- Operations that can modify the system must require explicit approval

## Documentation

- docs/DEVELOPER_PREVIEW.md
- docs/VM_GPU_GUIDE.md
- release/AXON_PREVIEW_READINESS_REPORT.md
- release/PUBLIC_RELEASE_MANIFEST.md

## Deferred Capabilities

The following features are planned but not enabled in this preview:

- Full GPU driver automation
- bitsandbytes installation
- ROCm setup
- Real dataset download workflow
- Training workflow execution
- ISO image release

## Vision

AXON OS is not just a desktop environment.

It is designed as an AI-driven operating layer capable of understanding user goals, managing intelligent workflows, running local AI models, automating development and analysis tasks, and providing offline-first AI capabilities.

Core philosophy:

Users should describe what they want. The system should determine how to achieve it.

## License

This project is protected under its respective license.

Unauthorized redistribution of proprietary internal systems is prohibited.

## Developer

Abdullah Ali
