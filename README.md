# AirBeat — Gesture-Controlled Virtual Instruments

Turn hand gestures into musical interaction using MediaPipe landmarks and cosine-similarity matching.

**MIT Global Appathon 2026 — Honorable Mention.** [Watch the demonstration](https://youtu.be/4Mvf6UDyCTw).

## Technical approach

The gesture-to-sound engine represents tracked landmarks as vectors, compares gestures with templates using cosine similarity, and triggers instrument sounds. Kawin Chamnanchak contributed the reusable core engine and Cajon interaction, sharing the API across three instruments.

## Repository guide

- `python_logic_instruments/`: instrument implementations, including Cajon, Guitar, Piano, and Ukulele directories.
- `templates/`: gesture templates.
- `main.py`: Python entry point.
- `app/`: web application.
- `mit-app-inventor/` and `plugin/`: integration work.

## Running the project

Start by inspecting `main.py` and the selected instrument implementation for dependencies, camera configuration, and sound/template paths. The web application dependencies are listed in `package.json`. A clean-install command sequence has not yet been verified; hardware, camera access, and audio output are needed for interactive use.

## Team and recognition

A team project by Kawin Chamnanchak, Parn Keskarn, and Pankan Kruemkangplu. The MIT App Inventor demonstration identifies the team and its 2026 Honorable Mention. Please retain teammate and third-party attribution when reusing this work.
