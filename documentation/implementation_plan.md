# Loomis AI — Implementation Plan & Architectural Roadmap

## 1. Executive Summary & Product Vision
Loomis AI is an artistic computer-vision engine and interactive drawing studio that reconstructs portrait drawings from underlying cranial geometry using Andrew Loomis' classical 3D structural drawing method. Rather than applying an edge-detection filter or generic template, the engine:
1. Detects 478 MediaPipe facial landmarks and extracts 3D head pose (Yaw, Pitch, Roll).
2. Computes the subject's unique cranial ball, brow equator, side plane truncation, eye plane, and mandible arc in image space.
3. Renders 20 progressive, authentic graphite drawing construction stages (from faint 4H cranial ball up to a rich 6B finished portrait).
4. Delivers an interactive studio workspace (scrubber, side-by-side comparison, split curtain, onion skinning, and high-res export).

---

## 2. Baseline Repository Audit

### 2.1 Directory Structure
```
LoomisAI/
├── .venv/                      # Active Python 3.12 virtual environment (MediaPipe 1.0.1, OpenCV, NumPy, Pillow)
├── ai-engine/
│   ├── input/
│   │   ├── reference.jpg       # Baseline portrait reference photo
│   │   └── uploads/            # Runtime user-uploaded portrait photos
│   ├── models/
│   │   └── face_landmarker.task # 3.7MB MediaPipe FaceLandmarker model file
│   ├── output/
│   │   ├── analysis.json       # 478 landmarks, head pose, aspect ratio, measurements
│   │   ├── construction.json   # 3D Loomis construction geometry (v4.0)
│   │   └── hand_drawn/         # 20 rendered graphite stage PNGs (stage_01.png - stage_20.png)
│   └── src/
│       ├── landmark_analyzer.py        # MediaPipe face landmark detection
│       ├── pose_estimator.py           # Head pose yaw/pitch/roll calculation
│       ├── face_analyzer.py            # Unified analysis coordinator
│       ├── loomis_geometry.py          # 3D Loomis geometric calculations
│       ├── graphite_quality.py         # Pencil grain, texture, variable line weight
│       ├── hand_drawn_renderer.py      # Core hand-drawn Loomis renderer
│       ├── stage_08_eye_construction.py
│       ├── stage_09_eye_eyelid_construction.py
│       ├── stage_10_eyebrow_construction.py
│       ├── stage_11_nose_construction.py
│       ├── stage_12_mouth_construction.py
│       ├── stage_13_cheek_forehead_contours.py
│       ├── stage_14_ear_construction.py
│       ├── stage_15_hairline_hair_mass.py
│       ├── stage_16_neck_construction.py
│       ├── stage_17_facial_contour_refinement.py
│       ├── stage_18_shadow_structures.py
│       ├── stage_19_secondary_details.py
│       ├── stage_20_final_portrait.py
│       ├── pipeline_runner.py          # End-to-end 20-stage pipeline orchestrator
│       └── server.py                   # Python HTTP API server & static file host
├── web/
│   ├── index.html                      # Interactive web studio layout
│   ├── style.css                       # Graphite studio theme & layout styles
│   └── app.js                          # Studio client logic, canvas viewer, mode switcher
└── documentation/
    └── implementation_plan.md          # This implementation plan
```

### 2.2 Reusable Working Components
- **MediaPipe Tasks Pipeline (`landmark_analyzer.py`, `face_analyzer.py`, `pose_estimator.py`)**: Fully working with `models/face_landmarker.task`. Accurately detects 478 3D landmarks and calculates Euler angles (Yaw, Pitch, Roll).
- **Loomis Geometric Engine (`loomis_geometry.py`)**: Generates v4.0 `construction.json` containing cranial sphere, central vertical axis, brow line, eye plane, mandible jaw bucket, and feature keystones.
- **Graphite Simulation Engine (`graphite_quality.py`)**: Simulates 4H to 6B pencil lead dynamics, paper grain tooth, variable line pressure, and stroke antialiasing.
- **Stage Renderers (Stages 1–20)**: Complete individual stage modules (`stage_08` through `stage_20`) implementing progressive drawing anatomy and photo-contour extraction.
- **Unified Pipeline Runner (`pipeline_runner.py`)**: Runs all 20 stages end-to-end on `reference.jpg` in ~16.85 seconds.

### 2.3 Identified Baseline Issues
1. **Stage 9 / HandDrawnLoomisRenderer Integration Issue**:
   - `HandDrawnLoomisRenderer.render_stage(self, stage_number, stage_name)` strictly required two positional arguments. Any caller executing `hdr.render_stage(9)` or omitting `stage_name` threw a `TypeError`.
   - `hand_drawn_renderer.py` internal `STAGES` dictionary only registered stages 1–7. Stages 8 and 9 were not mapped or dispatched within `HandDrawnLoomisRenderer`.
   - The CLI argument parser restricted `--stage` to `choices=range(1, 8)`, rejecting stages 8–20.
2. **Backend Architecture**:
   - `server.py` is an `http.server.HTTPServer` implementation that processes synchronously, which blocks if multiple requests occur. Needs robust async job tracking and error responses.
3. **Frontend Architecture**:
   - Currently a vanilla JavaScript studio (`web/app.js`). As requested in the product specifications, a modern, polished React + Tailwind CSS + Framer Motion frontend will be constructed with full component modularity, transitions, and state management.

---

## 3. Prioritized Implementation Roadmap

### Milestone 1 — Repository Audit & Baseline Verification (Current)
- Complete directory and code audit.
- Document working components and root cause of Stage 9 integration bug.
- Commit implementation plan to `documentation/implementation_plan.md`.

### Milestone 2 — Stabilize the AI Engine & Fix Stage 9
- Update `HandDrawnLoomisRenderer.render_stage(self, stage_number, stage_name=None)` to make `stage_name` optional with fallback to `STAGES.get(stage_number)`.
- Wire `HandDrawnLoomisRenderer.render_stage()` to dispatch Stage 8 (`Stage8EyeConstruction`), Stage 9 (`Stage09EyeRenderer`), and stages 10–20.
- Update `STAGES` mapping in `hand_drawn_renderer.py` to cover all 20 stages.
- Update CLI argument parser to support stages 1–20.
- Verify Stage 9 renders correctly both standalone and through `HandDrawnLoomisRenderer`.

### Milestone 3 — Pipeline & Stage Integration Verification
- Execute end-to-end regression tests across all 20 stages.
- Verify coordinate transformations, landmark anchoring, and visual output fidelity across varying portrait inputs.
- Add test scripts to validate stage image existence, dimensions, and visual structure.

### Milestone 4 — Engine Interface & Error Handling
- Formalize a clean Python API entrypoint (`ai_engine_api.py` / `LoomisPipeline`) accepting file path/buffers and options, returning structured JSON progress and results.
- Add explicit error boundaries for invalid images, missing faces, multi-face detections, and extreme rotations.

### Milestone 5 — High-Performance Backend Service
- Harden the API server to support multipart upload, validation, asynchronous pipeline execution, job status polling (`/api/jobs/:id`), stage metadata retrieval (`/api/stages-info`), and stage asset streaming.

### Milestone 6 — React + Tailwind + Framer Motion Frontend
- Scaffold modern React application with Tailwind CSS and Framer Motion.
- Build Landing Page, Upload Workspace with drag-and-drop & instant validation, Analysis Viewer with 3D pose visualization, and Interactive Drawing Workspace (Curtain split, side-by-side, onion skinning, scrubber playback, high-res export).

### Milestone 7 — End-to-End Integration & Visual Quality Verification
- Connect React frontend to the backend API.
- Test uploading novel portrait images with diverse skin tones, hairstyles, head angles, and lighting.
- Verify full 20-stage progression visually in the browser.

### Milestone 8 — Polish, Documentation & Handoff
- Refine animations, paper textures, keyboard shortcuts (Spacebar for play/pause, Left/Right arrows for stage navigation).
- Finalize documentation and user guide.
