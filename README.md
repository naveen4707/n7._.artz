# Loomis AI — Master 20-Stage Classical Portrait Drawing Studio

> **Transform ANY human portrait photo into 20 authentic, progressive hand-drawn graphite drawing steps following the classical Andrew Loomis Method.**

---

## 🌟 Overview & Key Architectural Upgrades

Loomis AI is an artistic computer-vision engine and interactive drawing studio. Unlike generic filter apps that apply simplistic edge detection or synthetic hardcoded formulas, Loomis AI combines:

1. **3D Cranial Structural Armature (Stages 1–7)**:
   - MediaPipe 478-point 3D landmark mesh & head pose estimation (Yaw, Pitch, Roll).
   - Andrew Loomis cranial sphere, brow equator, side plane truncation, and mandible bucket handle.
2. **Anatomical Feature Construction (Stages 8–14)**:
   - Orbital socket placement, eyelid curvature, pupils with specular highlights, eyebrow arches, 4-plane nose wedge, and Cupid's bow oral fissure.
3. **Dynamic Photo-Accurate Outlines (Stages 15–20)**:
   - **Dynamic Hair Mass & Silhouette (Stage 15)**: Bilateral filtering + Douglas-Peucker simplification + Catmull-Rom splines extract the true crown volume, partition, and framing locks of the uploaded subject.
   - **True Neck & Garment Outlines (Stage 16)**: Dynamically extracts the cylindrical neck, shoulders, collar, necklace/choker, and dress/saree drapery contours directly from the uploaded photo.
   - **Facial Contour Refinement & Bindi/Beauty Marks (Stage 17)**: Analyzes local forehead contrast to detect authentic marks without forcing them onto subjects who don't have them.
   - **Luminance-Aware Cast Shadows (Stage 18)**: Analyzes cheek gradient lighting to angle under-chin cast shadows to match actual illumination.
   - **Secondary Details (Stage 19)**: Captures intricate jewelry facets, fabric weave rhythms, and escaping hair wisps.
   - **Master Graphite Synthesis (Stage 20)**: Harmonizes faint underlying construction lines with rich 6B graphite portraiture.

---

## 🚀 Quick Start — Running the Web Studio

### 1. Start the Studio Server
From the project root:
```powershell
& "e:\LoomisAI\.venv\Scripts\python.exe" ai-engine/src/server.py --port 8000
```

### 2. Open the Studio in Your Browser
Visit: **[http://localhost:8000/](http://localhost:8000/)**

### 3. Studio Features:
- **Interactive Scrubber & Step Player**: Scrub smoothly through Stage 1 to Stage 20, or hit **Play** (or press `Spacebar`) to watch the portrait construct itself step-by-step.
- **Curtain Split Slider**: Drag the interactive curtain across the drawing to reveal the underlying reference photo.
- **Side-by-Side Mode**: Compare the reference portrait and the drawing side-by-side with synchronized zoom.
- **Onion Skinning**: Blend drawing opacity over the original photo from 0% to 100%.
- **Upload Any Portrait**: Drag-and-drop any human portrait photo (men, women, children, any hair or clothing style) to generate all 20 stages in under 10 seconds.
- **High-Res Export**: 1-click download of any stage PNG for printing or tracing.

---

## 📱 Mobile App Architecture (Flutter / React Native)

For launching as an iOS and Android mobile app:
- **Camera Screen**: Real-time oval face guide overlay to assist users in snapping centered, well-lit portraits.
- **On-Device / Cloud Pipeline**:
  - *Option A (Cloud API)*: Mobile app captures photo and sends a `POST /api/process` to the Loomis AI backend server, receiving the 20 stage PNG URLs.
  - *Option B (On-Device TFLite)*: Export the MediaPipe landmarker and OpenCV Canny/Spline pipeline into a Flutter C++ FFI plugin for completely offline portrait drawing generation.
- **Mobile Touch Scrubber**: Haptic feedback on each stage transition (1–20) as the user scrubs with their thumb.

---

## 📐 The 20 Classical Loomis Stages

| Stage | Name | Pencil | Focus |
|:---:|:---|:---:|:---|
| **01** | Cranial Sphere & Head Tilt | `4H` | Primary cranial ball & spatial orientation |
| **02** | Brow Line & Center Axis | `4H` | Spherical equator & facial centerline |
| **03** | Eye Plane & Side Sphere | `2H` | Lateral disc truncation & eye level |
| **04** | Jaw Construction | `2H` | Mandible bucket handle & chin rhythm |
| **05** | Nose Keystones | `H` | Midface proportion & rule of thirds |
| **06** | Mouth Rhythm | `H` | Dental arc cylinder & oral fissure |
| **07** | Unified Loomis Armature | `HB` | Complete 3D geometric scaffolding |
| **08** | Orbital Sockets | `HB` | Eye cavities within the skull |
| **09** | Eyelids, Iris & Pupils | `2B` | Palpebral fold, dark pupil, catchlight |
| **10** | Eyebrow Arches | `B` | Superciliary bone shelf & hair rhythm |
| **11** | Sculpted Nose | `2B` | Wedge planes, alar wings, nostrils |
| **12** | Cupid's Bow & Lips | `2B` | Vermilion border & lip cushions |
| **13** | Zygomatic Cheeks | `HB` | Cheekbone landmarks & temporal lines |
| **14** | Ear Architecture | `HB` | Helix, antihelix, concha, lobes |
| **15** | Hairline & Hair Mass | `4B` | Real hair silhouette & crown volume |
| **16** | Neck & Garment Outlines | `2B` | Neck cylinder, shoulders, dress drapery |
| **17** | Facial Refinement | `3B` | Authentic contours, bindi/marks |
| **18** | Major Shadow Structures | `4B` | Lighting-angled cast shadow tone |
| **19** | Secondary Details | `5B` | Fabric folds, jewelry, hair wisps |
| **20** | Master Graphite Portrait | `6B` | Final synthesis with subtle armature |
