# Native Refactor

This folder contains the new Windows-native refactor direction:

- `WinUI 3` for the desktop UI
- `Windows ML` for execution-provider bootstrap and Windows-native local inference
- `OpenVINO` model pipeline for better robustness than the previous Python desktop stack

## Why this refactor exists

The previous Python implementation was useful for rapid iteration, but it hit a ceiling in:

- robustness when the user looked tired or naturally opened their eyes less
- single-eye occlusion handling
- distance changes
- deployment size and packaging stability

The native refactor solves that by moving to a dedicated multi-stage pipeline:

1. face detection
2. landmarks / eye region extraction
3. eye-state classification
4. head-pose filtering
5. blink event state machine

## Development prerequisites

Build this on a Windows machine with:

- Visual Studio 2022
- .NET 8 SDK
- Windows application development workload
- Windows App SDK compatible toolchain

## Current scope

This first pass intentionally focuses on:

- project structure
- WinUI 3 shell
- Windows ML bootstrap entry point
- OpenVINO model folder contract
- view model / service layering

The next implementation pass should happen on a Windows dev box, where the app can be compiled and the camera pipeline can be validated end-to-end.
