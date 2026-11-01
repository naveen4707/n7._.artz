"""
LOOMIS AI — BACKEND REST API & STUDIO SERVER
Serves the web application and handles image processing for any portrait photo:
- POST /api/process: upload an image file or base64 and generate all 20 Loomis stages
- GET /api/stages-info: returns metadata and descriptions for all 20 stages
- GET /api/presets: returns demo portraits
- GET /output/hand_drawn/*: serves stage PNG images
- GET /input/*: serves reference & uploaded images
- Serves the frontend web studio from e:/LoomisAI/web
"""

from __future__ import annotations

import base64
import io
import json
import mimetypes
import os
import shutil
import sys
import time
from http import HTTPStatus
try:
    from http.server import ThreadingHTTPServer as HTTPServerBase
except ImportError:
    from http.server import HTTPServer as HTTPServerBase
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
LOOMIS_ROOT = AI_ENGINE_DIR.parent
WEB_DIR = LOOMIS_ROOT / "web"
SRC_DIR = AI_ENGINE_DIR / "src"
INPUT_DIR = AI_ENGINE_DIR / "input"
UPLOADS_DIR = INPUT_DIR / "uploads"
OUTPUT_DIR = AI_ENGINE_DIR / "output"
HAND_DRAWN_DIR = OUTPUT_DIR / "hand_drawn"
JOBS_DIR = LOOMIS_ROOT / "output" / "jobs"

# Ensure dirs exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
HAND_DRAWN_DIR.mkdir(parents=True, exist_ok=True)
WEB_DIR.mkdir(parents=True, exist_ok=True)
JOBS_DIR.mkdir(parents=True, exist_ok=True)

# Add src to sys.path
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from pipeline_runner import LoomisPipeline
from lesson_curriculum import LESSON_CURRICULUM, get_stage_curriculum, verify_stage_checkpoint

STAGE_METADATA: List[Dict[str, Any]] = [
    {
        "stage": 1,
        "title": "Cranial Sphere & Head Tilt",
        "category": "Loomis Foundation",
        "pencil": "4H Extra Hard Graphite",
        "loomisPrinciple": "The ball of the head is the primary cranial anchor. Everything hangs from this primary 3D sphere.",
        "drawingAction": "Sketch a clean sphere representing the cranial mass. Keep strokes feather-light so they can easily be built upon.",
        "hardnessBadge": "4H",
    },
    {
        "stage": 2,
        "title": "Brow Line & Central Facial Axis",
        "category": "Loomis Foundation",
        "pencil": "4H Hard Graphite",
        "loomisPrinciple": "The horizontal brow line wraps around the sphere. The vertical axis marks the exact center of the face in perspective.",
        "drawingAction": "Wrap the brow equator and the vertical centerline across the curved spherical surface following the head's exact tilt.",
        "hardnessBadge": "4H",
    },
    {
        "stage": 3,
        "title": "Eye Plane & Side Cranium Flattening",
        "category": "Loomis Foundation",
        "pencil": "2H Hard Graphite",
        "loomisPrinciple": "The human skull is not a perfect sphere; the sides are flattened by slicing off vertical discs where the ears attach.",
        "drawingAction": "Establish the side plane circle and drop the eye plane line below the brow line.",
        "hardnessBadge": "2H",
    },
    {
        "stage": 4,
        "title": "Jaw Construction & Mandible Rhythm",
        "category": "Loomis Foundation",
        "pencil": "2H Hard Graphite",
        "loomisPrinciple": "The jaw hangs from the ears and attaches to the cranial sphere like a bucket handle swinging into perspective.",
        "drawingAction": "Draw sweeping curves down from the temples to the gonial angle and meet at the chin wedge.",
        "hardnessBadge": "2H",
    },
    {
        "stage": 5,
        "title": "Nose Keystones & Midface Proportion",
        "category": "Loomis Foundation",
        "pencil": "H Graphite",
        "loomisPrinciple": "Rule of Thirds: Hairline to brow, brow to nose base, nose base to bottom of chin are approximately equal.",
        "drawingAction": "Mark the nasal septum base at precisely the 1/3 division along the central facial axis.",
        "hardnessBadge": "H",
    },
    {
        "stage": 6,
        "title": "Mouth Rhythm & Dental Arc",
        "category": "Loomis Foundation",
        "pencil": "H Graphite",
        "loomisPrinciple": "The mouth sits on a cylindrical muzzle (the dental arc) wrapping across the facial curvature.",
        "drawingAction": "Place the oral fissure 1/3 down from the nose base to the chin along the cylindrical contour.",
        "hardnessBadge": "H",
    },
    {
        "stage": 7,
        "title": "Unified Loomis Structural Armature",
        "category": "Loomis Foundation",
        "pencil": "HB Medium Graphite",
        "loomisPrinciple": "Step back and verify all proportional relationships and perspective angles before placing anatomical features.",
        "drawingAction": "Review the complete 3D armature in space; ensure perspective, tilt, and facial planes are firmly locked.",
        "hardnessBadge": "HB",
    },
    {
        "stage": 8,
        "title": "Orbital Socket & Eye Encasement",
        "category": "Anatomical Features",
        "pencil": "HB Medium Graphite",
        "loomisPrinciple": "Eyes are spheres nestled deep within the bony cavern of the orbital sockets underneath the brow shelf.",
        "drawingAction": "Block in the almond contour of the sclera and tear ducts resting securely inside the eye socket.",
        "hardnessBadge": "HB",
    },
    {
        "stage": 9,
        "title": "Eyelid Curvature, Iris & Pupils",
        "category": "Anatomical Features",
        "pencil": "2B Soft Graphite",
        "loomisPrinciple": "The upper eyelid wraps over the sphere of the eyeball. The pupil anchors the gaze and soul of the portrait.",
        "drawingAction": "Carve the dark pupil core, leave a crisp specular highlight, and define the palpebral crease folds.",
        "hardnessBadge": "2B",
    },
    {
        "stage": 10,
        "title": "Eyebrow Arches & Superciliary Ridge",
        "category": "Anatomical Features",
        "pencil": "B Graphite",
        "loomisPrinciple": "Eyebrows follow the bone shelf of the superciliary ridge, growing thicker at the head and tapering at the tail.",
        "drawingAction": "Stroke in the natural directional rhythm of the brow hairs along the anatomical bone ridge.",
        "hardnessBadge": "B",
    },
    {
        "stage": 11,
        "title": "Sculpted Nose Architecture",
        "category": "Anatomical Features",
        "pencil": "B / 2B Graphite",
        "loomisPrinciple": "The nose is a 4-sided wedge: bridge, two sloping side planes, and an undercut ball tip with nostrils.",
        "drawingAction": "Refine the lateral alar wings, the infratip lobule, and dark crescent nostrils.",
        "hardnessBadge": "2B",
    },
    {
        "stage": 12,
        "title": "Cupid's Bow & Anatomical Lip Structure",
        "category": "Anatomical Features",
        "pencil": "2B Soft Graphite",
        "loomisPrinciple": "Upper lip consists of 3 nodes; lower lip consists of 2 cylindrical cushions. The wet line gives depth.",
        "drawingAction": "Sculpt the vermilion border, Cupid's bow, and the philtrum column connecting to the nose base.",
        "hardnessBadge": "2B",
    },
    {
        "stage": 13,
        "title": "Zygomatic Cheeks & Forehead Planar Contours",
        "category": "Facial Contours",
        "pencil": "HB Graphite",
        "loomisPrinciple": "The cheekbone is the high landmark that catches the light; temporal ridges define the front face plane.",
        "drawingAction": "Trace the subtle transitions along the zygomatic arch and the temporal lines of the forehead.",
        "hardnessBadge": "HB",
    },
    {
        "stage": 14,
        "title": "Ear Architecture & Lobule Placement",
        "category": "Facial Contours",
        "pencil": "HB Graphite",
        "loomisPrinciple": "The ear aligns between the brow line and the nose base along the side-plane axis.",
        "drawingAction": "Construct the outer helix rim, the inner antihelix Y-shape, the concha bowl, and ear ornaments.",
        "hardnessBadge": "HB",
    },
    {
        "stage": 15,
        "title": "Hairline & True Hair Mass Silhouette",
        "category": "Hair & Silhouette",
        "pencil": "2B / 4B Soft Graphite",
        "loomisPrinciple": "Hair is drawn in large rhythmic masses and volumes that drape over the skull, not individual hairs.",
        "drawingAction": "Capture the true volume of the hair mass, the natural hairline rhythm, and framing locks from the photo.",
        "hardnessBadge": "4B",
    },
    {
        "stage": 16,
        "title": "Neck Cylinder & Garment Neckline",
        "category": "Anatomy & Drapery",
        "pencil": "2B Soft Graphite",
        "loomisPrinciple": "The neck is a cylinder inclined slightly forward, flanked by the sternocleidomastoid muscles and trapezius.",
        "drawingAction": "Construct the neck cylinder and draw the neckline, collar, and primary shoulder drape.",
        "hardnessBadge": "2B",
    },
    {
        "stage": 17,
        "title": "Facial Contour Refinement & Identifying Marks",
        "category": "Refinement & Likeness",
        "pencil": "3B Soft Graphite",
        "loomisPrinciple": "Harmonize individual features with the subject's distinct anatomical character and facial proportions.",
        "drawingAction": "Refine delicate transitions and render authentic identifying marks (such as a bindi or beauty marks if present).",
        "hardnessBadge": "3B",
    },
    {
        "stage": 18,
        "title": "Major Shadow Structures & Lighting Tone",
        "category": "Value & Lighting",
        "pencil": "4B Soft Graphite",
        "loomisPrinciple": "Separate light and shadow with clear terminator lines. Cast shadows anchor form to the page.",
        "drawingAction": "Cross-hatch the under-chin cast shadow and eye socket core shadows with angled graphite tone matching the lighting.",
        "hardnessBadge": "4B",
    },
    {
        "stage": 19,
        "title": "Secondary Details, Drapery Folds & Hair Wisps",
        "category": "Details & Textures",
        "pencil": "3B / 5B Velvet Graphite",
        "loomisPrinciple": "Add the rhythmic secondary accents that bring vitality without destroying the primary masses.",
        "drawingAction": "Lay down rhythmic fabric folds, fine escaping hair wisps, and delicate jewelry accents.",
        "hardnessBadge": "5B",
    },
    {
        "stage": 20,
        "title": "Master Graphite Portrait & Loomis Synthesis",
        "category": "Masterpiece Finish",
        "pencil": "6B Deep Velvet Charcoal & Graphite",
        "loomisPrinciple": "The ultimate synthesis of structural foundation, anatomical accuracy, and artistic expression.",
        "drawingAction": "Final balance: subtle foundation lines visible underneath rich, velvety graphite portraiture.",
        "hardnessBadge": "6B",
    },
]


class LoomisRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP handler serving Loomis Web Studio and API endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(LOOMIS_ROOT), **kwargs)

    def do_OPTIONS(self):
        self.send_response(HTTPStatus.OK)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_HEAD(self):
        self.do_GET()

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path in ("/", "/index.html"):
            index_path = WEB_DIR / "index.html"
            if index_path.exists():
                return self._serve_file(index_path, "text/html; charset=utf-8")
            else:
                return self._send_json({"error": "Web frontend not found."}, status=HTTPStatus.NOT_FOUND)

        if path in ("/sw.js", "/manifest.json", "/favicon.ico"):
            target = WEB_DIR / path.lstrip("/")
            if target.exists() and target.is_file():
                mime, _ = mimetypes.guess_type(str(target))
                return self._serve_file(target, mime or "application/javascript")

        if path.startswith("/web/"):
            rel_file = path[5:]
            target = WEB_DIR / rel_file
            if target.exists() and target.is_file():
                mime, _ = mimetypes.guess_type(str(target))
                return self._serve_file(target, mime or "application/octet-stream")

        if path == "/api/status":
            return self._send_json({
                "status": "online",
                "engine": "Loomis AI Master 20-Stage Pipeline",
                "ready": True,
                "stagesCount": 20,
                "defaultImage": "reference.jpg",
            })

        if path == "/api/stages-info":
            # Add availability flag to each stage
            params = parse_qs(parsed.query)
            target_job_id = params.get("job_id", [None])[0]
            job_stages_dir = (JOBS_DIR / target_job_id / "stages") if target_job_id else None

            stages_with_status = []
            for item in STAGE_METADATA:
                num = item["stage"]
                fn = f"stage_{num:02d}.png"
                if job_stages_dir and (job_stages_dir / fn).exists():
                    url = f"/api/jobs/{target_job_id}/stages/{fn}?t={int(time.time())}"
                    exists = True
                else:
                    exists = (HAND_DRAWN_DIR / fn).exists()
                    url = f"/output/hand_drawn/{fn}?t={int(time.time())}" if exists else None
                stages_with_status.append({
                    **item,
                    "url": url,
                    "filename": fn,
                    "generated": exists,
                })
            return self._send_json({"stages": stages_with_status})

        if path == "/api/lesson/curriculum":
            return self._send_json({"stages": LESSON_CURRICULUM})

        if path.startswith("/api/lesson/stage/"):
            try:
                stage_num = int(path.split("/")[-1])
                curr = get_stage_curriculum(stage_num)
                if curr:
                    return self._send_json(curr)
                return self._send_json({"error": f"Stage {stage_num} curriculum not found"}, status=HTTPStatus.NOT_FOUND)
            except ValueError:
                return self._send_json({"error": "Invalid stage number"}, status=HTTPStatus.BAD_REQUEST)

        if path == "/api/presets":
            presets = []
            ref = INPUT_DIR / "reference.jpg"
            if ref.exists():

                presets.append({
                    "id": "reference",
                    "name": "Classical Royal Portrait (Indian Saree)",
                    "url": "/input/reference.jpg",
                    "bwUrl": "/input/reference_bw.jpg",
                    "filename": "reference.jpg",
                })
            # Add any other image files in input/ excluding _bw
            for f in INPUT_DIR.glob("*.jpg"):
                if f.name != "reference.jpg" and not f.stem.endswith("_bw"):
                    bw_name = f"{f.stem}_bw{f.suffix}"
                    presets.append({
                        "id": f.stem,
                        "name": f.stem.replace("_", " ").title(),
                        "url": f"/input/{f.name}",
                        "bwUrl": f"/input/{bw_name}" if (INPUT_DIR / bw_name).exists() else f"/input/{f.name}",
                        "filename": f.name,
                    })
            for f in INPUT_DIR.glob("*.png"):
                if not f.stem.endswith("_bw"):
                    presets.append({
                        "id": f.stem,
                        "name": f.stem.replace("_", " ").title(),
                        "url": f"/input/{f.name}",
                        "bwUrl": f"/input/{f.name}",
                        "filename": f.name,
                    })
            return self._send_json({"presets": presets})

        if path.startswith("/output/hand_drawn/"):
            fname = path.split("/")[-1]
            fpath = HAND_DRAWN_DIR / fname
            if fpath.exists() and fpath.is_file():
                return self._serve_file(fpath, "image/png")
            else:
                return self._send_json({"error": "Stage image not found"}, status=HTTPStatus.NOT_FOUND)

        if path == "/api/validation":
            val_file = OUTPUT_DIR / "validation.json"
            if not val_file.exists():
                val_file = JOBS_DIR / "reference_job" / "validation.json"
            if val_file.exists():
                with open(val_file, "r", encoding="utf-8") as f:
                    return self._send_json(json.load(f))
            return self._send_json({"error": "Validation report not found"}, status=HTTPStatus.NOT_FOUND)

        if path == "/api/jobs":
            jobs_list = []
            if JOBS_DIR.exists():
                for jdir in sorted(JOBS_DIR.iterdir(), key=lambda p: p.stat().st_mtime if p.is_dir() else 0, reverse=True):
                    if jdir.is_dir():
                        mf = jdir / "manifest.json"
                        if mf.exists():
                            try:
                                with open(mf, "r", encoding="utf-8") as f:
                                    mdata = json.load(f)
                                jobs_list.append({
                                    "job_id": jdir.name,
                                    "created_at": mdata.get("created_at"),
                                    "elapsed_seconds": mdata.get("elapsed_seconds"),
                                    "source_image": mdata.get("source_image", {}),
                                    "validation_score": mdata.get("validation_summary", {}).get("overall_score"),
                                    "status": mdata.get("validation_summary", {}).get("status"),
                                    "manifest_url": f"/api/jobs/{jdir.name}/manifest",
                                    "zip_url": f"/api/jobs/{jdir.name}/download-zip",
                                })
                            except Exception:
                                pass
            return self._send_json({"jobs": jobs_list})

        if path.startswith("/api/jobs/"):
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 3:
                job_id = parts[2]
                jdir = JOBS_DIR / job_id
                if not jdir.exists():
                    return self._send_json({"error": f"Job {job_id} not found"}, status=HTTPStatus.NOT_FOUND)

                if len(parts) == 3 or (len(parts) == 4 and parts[3] in ("manifest", "manifest.json")):
                    mf = jdir / "manifest.json"
                    if mf.exists():
                        with open(mf, "r", encoding="utf-8") as f:
                            return self._send_json(json.load(f))
                    return self._send_json({"error": "Manifest not found"}, status=HTTPStatus.NOT_FOUND)

                if len(parts) == 4 and parts[3] in ("validation", "validation.json"):
                    vf = jdir / "validation.json"
                    if vf.exists():
                        with open(vf, "r", encoding="utf-8") as f:
                            return self._send_json(json.load(f))
                    return self._send_json({"error": "Validation not found"}, status=HTTPStatus.NOT_FOUND)

                if len(parts) == 4 and parts[3] in ("download-zip", "zip"):
                    zip_files = list(jdir.glob("*.zip"))
                    if zip_files:
                        return self._serve_file(zip_files[0], "application/zip")
                    from output_generator import OutputGenerator
                    og = OutputGenerator(job_id=job_id, base_dir=JOBS_DIR)
                    zf = og.create_zip_archive()
                    return self._serve_file(zf, "application/zip")

                if len(parts) == 4 and parts[3] in ("original", "photo"):
                    for ext in (".jpg", ".jpeg", ".png", ".webp"):
                        orig = jdir / f"original{ext}"
                        if orig.exists():
                            mime, _ = mimetypes.guess_type(str(orig))
                            return self._serve_file(orig, mime or "image/jpeg")
                    return self._send_json({"error": "Original image not found"}, status=HTTPStatus.NOT_FOUND)

                if len(parts) == 4 and parts[3] in ("bw", "bw_reference", "bw_photo"):
                    for bw_name in ("bw_reference.jpg", "bw_reference.png"):
                        bw_f = jdir / bw_name
                        if bw_f.exists():
                            return self._serve_file(bw_f, "image/jpeg")
                    return self._send_json({"error": "B&W reference not found for this job"}, status=HTTPStatus.NOT_FOUND)

                if len(parts) == 5 and parts[3] == "stages":
                    stage_filename = parts[4]
                    sfile = jdir / "stages" / stage_filename
                    if sfile.exists():
                        return self._serve_file(sfile, "image/png")
                    return self._send_json({"error": f"Stage file {stage_filename} not found"}, status=HTTPStatus.NOT_FOUND)

        if path.startswith("/input/"):
            rel_file = path[7:]
            fpath = INPUT_DIR / rel_file
            if fpath.exists() and fpath.is_file():
                mime, _ = mimetypes.guess_type(str(fpath))
                return self._serve_file(fpath, mime or "image/jpeg")
            else:
                return self._send_json({"error": "Input image not found"}, status=HTTPStatus.NOT_FOUND)

        # Fallback to default SimpleHTTPRequestHandler
        super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/lesson/verify-checkpoint":
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len)
                data = json.loads(body.decode("utf-8")) if body else {}
                stage_num = int(data.get("stage", 1))
                checks = data.get("checks", [])
                notes = data.get("notes", "")
                result = verify_stage_checkpoint(stage_num, checks, notes=notes)
                return self._send_json(result)
            except Exception as e:
                return self._send_json({"error": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if path == "/api/convert-bw":
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len)
                data = json.loads(body.decode("utf-8")) if body else {}
                img_data = data.get("image")
                if not img_data:
                    return self._send_json({"error": "Missing 'image' field"}, status=HTTPStatus.BAD_REQUEST)
                if "," in img_data:
                    img_data = img_data.split(",", 1)[1]
                raw_bytes = base64.b64decode(img_data)

                import cv2
                import numpy as np
                from bw_converter import convert_to_black_and_white

                nparr = np.frombuffer(raw_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is None:
                    return self._send_json({"error": "Invalid image data"}, status=HTTPStatus.BAD_REQUEST)

                ts = int(time.time() * 1000)
                temp_in = UPLOADS_DIR / f"temp_{ts}.jpg"
                temp_bw = UPLOADS_DIR / f"temp_{ts}_bw.jpg"
                cv2.imwrite(str(temp_in), img)
                convert_to_black_and_white(temp_in, temp_bw)

                with open(temp_bw, "rb") as f:
                    bw_b64 = base64.b64encode(f.read()).decode("ascii")

                try:
                    temp_in.unlink(missing_ok=True)
                except Exception:
                    pass

                return self._send_json({
                    "success": True,
                    "bwDataUrl": f"data:image/jpeg;base64,{bw_b64}",
                    "bwImageUrl": f"/input/uploads/{temp_bw.name}",
                })
            except Exception as e:
                import traceback
                traceback.print_exc()
                return self._send_json({"error": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if path == "/api/process-preset":
            try:
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len)
                data = json.loads(body.decode("utf-8")) if body else {}
                preset_name = data.get("filename", "reference.jpg")
                target_path = INPUT_DIR / preset_name
                if not target_path.exists():
                    return self._send_json({"error": f"Preset {preset_name} not found"}, status=HTTPStatus.NOT_FOUND)

                from bw_converter import get_bw_reference_path
                bw_path = get_bw_reference_path(target_path)
                bw_display_url = f"/input/{bw_path.name}"

                pipeline = LoomisPipeline(output_dir=HAND_DRAWN_DIR)
                res = pipeline.process(image_path=target_path)

                stages_res = []
                for item in STAGE_METADATA:
                    num = item["stage"]
                    fn = f"stage_{num:02d}.png"
                    stages_res.append({
                        **item,
                        "url": f"/output/hand_drawn/{fn}",
                        "filename": fn,
                        "generated": True,
                    })

                return self._send_json({
                    "success": True,
                    "elapsed_seconds": res.get("elapsed_seconds", 0),
                    "imageUrl": f"/input/{preset_name}",
                    "bwImageUrl": bw_display_url,
                    "pose": res.get("pose", {}),
                    "stages": stages_res,
                    "validation": res.get("validation", {}),
                })
            except Exception as e:
                import traceback
                traceback.print_exc()
                return self._send_json({"error": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

        if path == "/api/process":
            try:
                content_type = self.headers.get("Content-Type", "")
                target_path = None
                display_url = ""
                bw_display_url = ""

                if "application/json" in content_type:
                    content_len = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_len)
                    data = json.loads(body.decode("utf-8"))
                    img_data = data.get("image")
                    ext = data.get("format", "jpg").lower()

                    if not img_data:
                        return self._send_json({"error": "Missing 'image' field in JSON"}, status=HTTPStatus.BAD_REQUEST)

                    if "," in img_data:
                        img_data = img_data.split(",", 1)[1]

                    raw_bytes = base64.b64decode(img_data)
                    if len(raw_bytes) < 100:
                        return self._send_json({"error": "Uploaded image file is empty or invalid."}, status=HTTPStatus.BAD_REQUEST)

                    if ext not in ("jpg", "jpeg", "png", "webp"):
                        ext = "jpg"

                    timestamp = int(time.time())
                    filename = f"upload_{timestamp}.{ext}"
                    target_path = UPLOADS_DIR / filename
                    with open(target_path, "wb") as f:
                        f.write(raw_bytes)
                    display_url = f"/input/uploads/{filename}"

                elif "multipart/form-data" in content_type:
                    content_len = int(self.headers.get("Content-Length", 0))
                    raw_body = self.rfile.read(content_len)
                    boundary = None
                    for param in content_type.split(";"):
                        param = param.strip()
                        if param.startswith("boundary="):
                            boundary = param.split("=", 1)[1].strip('"\'')
                    if not boundary:
                        return self._send_json({"error": "Missing boundary in multipart request"}, status=HTTPStatus.BAD_REQUEST)

                    boundary_bytes = b"--" + boundary.encode("utf-8")
                    parts = raw_body.split(boundary_bytes)
                    img_bytes = None
                    for part in parts:
                        if not part or part.strip() in (b"", b"--"):
                            continue
                        header_data, sep, body_data = part.partition(b"\r\n\r\n")
                        if not body_data:
                            continue
                        if body_data.endswith(b"\r\n"):
                            body_data = body_data[:-2]
                        if b'name="image"' in header_data:
                            img_bytes = body_data
                            break

                    if not img_bytes:
                        return self._send_json({"error": "No 'image' field provided in multipart form-data"}, status=HTTPStatus.BAD_REQUEST)

                    timestamp = int(time.time())
                    filename = f"upload_{timestamp}.jpg"
                    target_path = UPLOADS_DIR / filename
                    with open(target_path, "wb") as f:
                        f.write(img_bytes)
                    display_url = f"/input/uploads/{filename}"

                else:
                    return self._send_json({"error": "Unsupported Content-Type. Use multipart/form-data or application/json"}, status=HTTPStatus.BAD_REQUEST)

                if not target_path or not target_path.exists():
                    return self._send_json({"error": "Failed to save uploaded image"}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

                # Convert uploaded photo into high-contrast Black & White picture
                from bw_converter import convert_to_black_and_white
                bw_filename = f"{target_path.stem}_bw.jpg"
                bw_target_path = UPLOADS_DIR / bw_filename
                convert_to_black_and_white(target_path, bw_target_path)
                bw_display_url = f"/input/uploads/{bw_filename}"

                job_id = f"job_{int(time.time())}_{os.urandom(3).hex()}"
                pipeline = LoomisPipeline(output_dir=HAND_DRAWN_DIR)
                res = pipeline.process(image_path=target_path, job_id=job_id)

                stages_res = []
                for item in STAGE_METADATA:
                    num = item["stage"]
                    fn = f"stage_{num:02d}.png"
                    stages_res.append({
                        **item,
                        "url": f"/api/jobs/{job_id}/stages/{fn}",
                        "legacy_url": f"/output/hand_drawn/{fn}?t={int(time.time())}",
                        "filename": fn,
                        "generated": True,
                    })

                return self._send_json({
                    "success": True,
                    "job_id": job_id,
                    "elapsed_seconds": res.get("elapsed_seconds", 0),
                    "imageUrl": display_url,
                    "bwImageUrl": bw_display_url,
                    "pose": res.get("pose", {}),
                    "stages": stages_res,
                    "validation": res.get("validation", {}),
                    "manifest": res.get("manifest", {}),
                    "zip_url": f"/api/jobs/{job_id}/download-zip",
                })

            except Exception as e:
                import traceback
                traceback.print_exc()
                return self._send_json({"error": str(e)}, status=HTTPStatus.INTERNAL_SERVER_ERROR)

        self._send_json({"error": "Not Found"}, status=HTTPStatus.NOT_FOUND)

    def _serve_file(self, path: Path, content_type: str) -> None:
        try:
            with open(path, "rb") as f:
                data = f.read()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, str(e))

    def _send_json(self, data: Any, status: int = HTTPStatus.OK) -> None:
        raw = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)


def run_server(port: int = 8000):
    server_address = ("127.0.0.1", port)
    httpd = HTTPServerBase(server_address, LoomisRequestHandler)
    print("=" * 60)
    print(f"  LOOMIS AI STUDIO SERVER IS RUNNING")
    print(f"  Local Web App:  http://localhost:{port}/")
    print(f"  REST API Base:  http://localhost:{port}/api/")
    print(f"  Static Root:    {LOOMIS_ROOT}")
    print("=" * 60)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")
        httpd.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Loomis AI Studio Server")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the studio server on")
    args = parser.parse_args()
    run_server(args.port)
