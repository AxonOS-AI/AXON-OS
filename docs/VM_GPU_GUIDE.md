# AXON VM and GPU Guide

This guide explains how AXON handles GPU acceleration when running on bare metal, inside virtual machines, or inside WSL2.

## Core Rule

AXON does not blindly install GPU drivers or GPU packages.

AXON first detects the runtime environment, then checks GPU visibility, then selects a safe acceleration policy.

## VMware and Virtual Machines

When AXON runs inside VMware or a similar VM, the guest system may only see a virtual GPU such as VMware SVGA.

In this case, AXON uses VM-safe CPU mode.

AXON will not automatically install GPU drivers, NVIDIA drivers, ROCm, or bitsandbytes inside a VM unless real GPU passthrough is confirmed.

## GPU Passthrough

GPU passthrough means the real physical GPU is exposed directly to the guest system.

Without passthrough, a VM usually cannot use the real GPU for AI acceleration.

With passthrough, AXON can detect the real GPU and then decide whether CUDA, ROCm, Vulkan, or CPU mode should be used.

## Windows Users

For Windows users who need GPU acceleration, AXON should recommend WSL2 mode when supported.

WSL2 is the preferred future path for many Windows users because it can provide Linux workflows while keeping Windows as the main operating system.

## NVIDIA Policy

AXON only allows optional NVIDIA CUDA packages after CUDA readiness is confirmed.

bitsandbytes is treated as an optional GPU package, not a required package.

nvidia-smi is treated as a driver tool and is not auto-installed by AXON.

## AMD Policy

AMD acceleration requires ROCm, Vulkan, or another supported backend depending on hardware and environment compatibility.

ROCm is not installed automatically in this Developer Preview.

## Safe Defaults

- VM without real GPU passthrough: VM-safe CPU mode
- NVIDIA with confirmed CUDA: CUDA path may be planned after approval
- AMD hardware: ROCm or alternative backend check required
- Unknown environment: CPU safe mode

## User Message

If AXON cannot use GPU acceleration, it should explain why and continue safely using CPU mode.

AXON must never break the user system while trying to enable acceleration.

## Credit

Developed by Abdullah Ali.
