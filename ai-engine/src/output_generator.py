"""
LOOMIS AI — OUTPUT GENERATOR & MANIFEST MANAGER

Manages organized per-job output directories, stage naming, manifest.json,
validation persistence, ZIP export, and backward-compatible paths.

Structure:
output/jobs/{job_id}/
    original.jpg
    analysis.json
    construction.json
    validation.json
    stages/
        stage_01_cranium.png
        stage_02_center_axis.png
        ...
        stage_20_final_portrait.png
    manifest.json
    stages_archive.zip
"""

from __future__ import annotations

import datetime
import json
import shutil
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_JOBS_DIR = PROJECT_ROOT / "output" / "jobs"
ENGINE_JOBS_DIR = AI_ENGINE_DIR / "output" / "jobs"

STAGE_DESCRIPTIONS: Dict[int, Dict[str, str]] = {
    1: {
        "slug": "cranium",
        "title": "Cranial Sphere & Head Tilt",
        "category": "Loomis Foundation",
        "pencil": "4H Extra Hard Graphite",
        "explanation": "The cranial ball is the primary 3D anchor of the human head, establishing spatial volume and perspective tilt.",
        "drawing_action": "Draw a clean sphere representing the cranial mass. Keep lines feather-light.",
    },
    2: {
        "slug": "center_axis",
        "title": "Brow Equator & Central Facial Axis",
        "category": "Loomis Foundation",
        "pencil": "4H Hard Graphite",
        "explanation": "The horizontal brow line wraps around the sphere's equator; the vertical centerline defines facial direction.",
        "drawing_action": "Wrap the brow equator and the vertical centerline across the sphere following head tilt.",
    },
    3: {
        "slug": "eye_plane",
        "title": "Eye Plane & Side Cranium Flattening",
        "category": "Loomis Foundation",
        "pencil": "2H Hard Graphite",
        "explanation": "The human skull is flattened at the temples; vertical disc truncation marks the ear placement plane.",
        "drawing_action": "Slice off the side plane disc and drop the horizontal eye plane below the brow equator.",
    },
    4: {
        "slug": "jaw",
        "title": "Jaw Construction & Mandible Rhythm",
        "category": "Loomis Foundation",
        "pencil": "2H Hard Graphite",
        "explanation": "The mandible swings down from the ears like a bucket handle, tapering down to the chin wedge.",
        "drawing_action": "Draw sweeping curves from temples to gonial angle and meet at the chin wedge.",
    },
    5: {
        "slug": "nose_keystone",
        "title": "Nose Keystones & Midface Proportion",
        "category": "Loomis Foundation",
        "pencil": "H Graphite",
        "explanation": "Rule of Thirds: establishes the nasal septum base at the middle third mark along the facial axis.",
        "drawing_action": "Mark the nasal septum keystone at the 1/3 division along the central facial axis.",
    },
    6: {
        "slug": "mouth_rhythm",
        "title": "Mouth Rhythm & Dental Arc Cylinder",
        "category": "Loomis Foundation",
        "pencil": "H Graphite",
        "explanation": "The mouth rests on a barrel-like dental cylinder wrapping across the facial curvature.",
        "drawing_action": "Place the oral fissure 1/3 down from the nose base to the chin along the cylindrical contour.",
    },
    7: {
        "slug": "unified_armature",
        "title": "Unified Loomis 3D Armature",
        "category": "Loomis Foundation",
        "pencil": "HB Graphite",
        "explanation": "Harmonizes all foundation planes into a coherent 3D scaffolding ready for anatomical feature placement.",
        "drawing_action": "Re-affirm major planes and check spatial alignment of brow, nose, and chin thirds.",
    },
    8: {
        "slug": "orbital_sockets",
        "title": "Orbital Sockets",
        "category": "Anatomical Features",
        "pencil": "HB Graphite",
        "explanation": "Blocks in the eye socket cavities recessed into the cranium beneath the brow bone shelf.",
        "drawing_action": "Carve out the orbital sockets with light, angled hexagonal construction lines.",
    },
    9: {
        "slug": "eyeball_and_eyelids",
        "title": "Eyeball and Eyelid Construction",
        "category": "Anatomical Features",
        "pencil": "2B Medium-Soft Graphite",
        "explanation": "Constructs the spherical eyeball, curving palpebral eyelid folds, tear duct, and dark pupil with catchlight.",
        "drawing_action": "Wrap upper and lower eyelids over the eyeball sphere; place pupil and specular highlight.",
    },
    10: {
        "slug": "eyebrow_arches",
        "title": "Eyebrow Arches",
        "category": "Anatomical Features",
        "pencil": "B Graphite",
        "explanation": "Follows the superciliary ridge of the frontal bone with directional hair growth rhythms.",
        "drawing_action": "Draw the eyebrow contour along the brow ridge with rhythmic pencil strokes.",
    },
    11: {
        "slug": "nose_refinement",
        "title": "Sculpted Nose Construction",
        "category": "Anatomical Features",
        "pencil": "2B Graphite",
        "explanation": "Constructs the 4-plane nose keystone: bridge, side sloping planes, ball of the nose, and nostril wings.",
        "drawing_action": "Define bridge planes, alar wings, and cast shadow beneath the nasal base.",
    },
    12: {
        "slug": "mouth_and_lips",
        "title": "Cupid's Bow & Lip Refinement",
        "category": "Anatomical Features",
        "pencil": "2B Graphite",
        "explanation": "Maps the 5 lip cushions: 3 on upper lip (including Cupid's bow) and 2 on lower lip over the dental arch.",
        "drawing_action": "Draw the oral fissure line of closure, Cupid's bow nodes, and philtrum columns.",
    },
    13: {
        "slug": "cheek_and_forehead",
        "title": "Zygomatic Cheeks & Temporal Lines",
        "category": "Anatomical Features",
        "pencil": "HB Graphite",
        "explanation": "Defines cheekbone contours and the temporal ridge separating face plane from cranium side plane.",
        "drawing_action": "Trace the zygomatic arches from ear to upper lip and define forehead boundaries.",
    },
    14: {
        "slug": "ear_construction",
        "title": "Ear Architecture",
        "category": "Anatomical Features",
        "pencil": "HB Graphite",
        "explanation": "Anchors the outer ear between brow line and nose base: helix rim, antihelix, tragus, and lobe.",
        "drawing_action": "Draw the C-curve of the helix and anchor the ear to the side plane vertical division.",
    },
    15: {
        "slug": "hairline_and_hair_mass",
        "title": "Hairline & Volumetric Hair Mass",
        "category": "Dynamic Outlines & Tone",
        "pencil": "4B Soft Graphite",
        "explanation": "Captures the authentic hair silhouette, crown volume, partition, and framing locks of the subject.",
        "drawing_action": "Block in the outer hair silhouette and rhythm lines radiating from crown/partition.",
    },
    16: {
        "slug": "neck_and_shoulders",
        "title": "Neck, Shoulders & Garment Drapery",
        "category": "Dynamic Outlines & Tone",
        "pencil": "2B Graphite",
        "explanation": "Anchors the head to the body via cervical cylinder, sternocleidomastoid muscles, clavicle, and dress lines.",
        "drawing_action": "Draw neck cylinder, collar lines, necklace/choker, and shoulder drapery curves.",
    },
    17: {
        "slug": "facial_contour_refinement",
        "title": "Facial Refinement & Authentic Marks",
        "category": "Dynamic Outlines & Tone",
        "pencil": "3B Graphite",
        "explanation": "Refines jaw and cheek edges to capture distinct individual likeness, including beauty marks or bindi.",
        "drawing_action": "Crispen facial boundary contours; place authentic forehead marks or dimples.",
    },
    18: {
        "slug": "shadow_structures",
        "title": "Luminance-Aware Shadow Structures",
        "category": "Dynamic Outlines & Tone",
        "pencil": "4B Soft Graphite",
        "explanation": "Analyzes reference illumination to lay in directional graphite cast shadows beneath chin and features.",
        "drawing_action": "Lay down unified directional shadow planes matching key light source.",
    },
    19: {
        "slug": "secondary_details",
        "title": "Secondary Details & Ornamentation",
        "category": "Dynamic Outlines & Tone",
        "pencil": "5B Soft Graphite",
        "explanation": "Renders intricate jewelry facets, fabric texture rhythms, and escaping hair wisps.",
        "drawing_action": "Add delicate graphite accents: jewelry sparkles, embroidery lines, fine eyelashes.",
    },
    20: {
        "slug": "final_portrait",
        "title": "Master Classical Graphite Portrait",
        "category": "Master Synthesis",
        "pencil": "6B Extra Soft Graphite",
        "explanation": "Harmonizes faint underlying Loomis armature with rich, expressive graphite portraiture.",
        "drawing_action": "Final tonal pass, deep graphite accents, subtle paper tooth unification.",
    },
}


class OutputGenerator:
    """
    Manages complete, structured job directories containing all outputs,
    validation reports, stage images, and manifest.json.
    """

    def __init__(self, job_id: str, base_dir: Optional[Path] = None) -> None:
        self.job_id = job_id
        self.base_dir = Path(base_dir) if base_dir else DEFAULT_JOBS_DIR
        self.job_dir = self.base_dir / self.job_id
        self.stages_dir = self.job_dir / "stages"

        self.job_dir.mkdir(parents=True, exist_ok=True)
        self.stages_dir.mkdir(parents=True, exist_ok=True)

    def save_source_image(self, source_path: Path) -> Path:
        """Copy source image into job directory."""
        dest = self.job_dir / f"original{source_path.suffix.lower()}"
        if source_path.resolve() != dest.resolve():
            shutil.copy2(source_path, dest)
        return dest

    def save_bw_image(self, bw_path: Path) -> Path:
        """Copy black-and-white converted image into job directory."""
        dest = self.job_dir / f"bw_reference{bw_path.suffix.lower()}"
        if bw_path.resolve() != dest.resolve():
            shutil.copy2(bw_path, dest)
        return dest

    def save_analysis(self, analysis: Dict[str, Any]) -> Path:
        dest = self.job_dir / "analysis.json"
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        return dest

    def save_construction(self, construction: Dict[str, Any]) -> Path:
        dest = self.job_dir / "construction.json"
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(construction, f, indent=2, ensure_ascii=False)
        return dest

    def save_validation(self, validation: Dict[str, Any]) -> Path:
        dest = self.job_dir / "validation.json"
        with open(dest, "w", encoding="utf-8") as f:
            json.dump(validation, f, indent=2, ensure_ascii=False)
        return dest

    def get_stage_path(self, stage_number: int, slug_named: bool = True) -> Path:
        info = STAGE_DESCRIPTIONS.get(stage_number, {"slug": f"stage_{stage_number}"})
        if slug_named:
            return self.stages_dir / f"stage_{stage_number:02d}_{info['slug']}.png"
        return self.stages_dir / f"stage_{stage_number:02d}.png"

    def record_stage_image(self, stage_number: int, image_file: Path) -> Dict[str, Path]:
        """
        Stores stage image with both canonical filenames:
        - stage_{num:02d}_{slug}.png
        - stage_{num:02d}.png
        """
        canonical = self.get_stage_path(stage_number, slug_named=True)
        alias = self.get_stage_path(stage_number, slug_named=False)

        if image_file.resolve() != canonical.resolve():
            shutil.copy2(image_file, canonical)
        if canonical.resolve() != alias.resolve():
            shutil.copy2(canonical, alias)

        return {"canonical": canonical, "alias": alias}

    def generate_manifest(
        self,
        analysis: Dict[str, Any],
        construction: Dict[str, Any],
        validation: Optional[Dict[str, Any]] = None,
        source_image_name: str = "original.jpg",
        elapsed_seconds: float = 0.0,
    ) -> Dict[str, Any]:
        """Generate comprehensive, structured manifest.json."""
        pose = analysis.get("pose", {})
        image_meta = analysis.get("image", {})

        stages_list: List[Dict[str, Any]] = []
        for stage_num in range(1, 21):
            desc = STAGE_DESCRIPTIONS[stage_num]
            c_file = self.get_stage_path(stage_num, slug_named=True)
            a_file = self.get_stage_path(stage_num, slug_named=False)
            exists = c_file.exists() or a_file.exists()

            stages_list.append({
                "stage": stage_num,
                "id": f"stage_{stage_num:02d}_{desc['slug']}",
                "title": desc["title"],
                "category": desc["category"],
                "pencil": desc["pencil"],
                "explanation": desc["explanation"],
                "drawing_action": desc["drawing_action"],
                "filename": f"stage_{stage_num:02d}.png",
                "canonical_filename": f"stage_{stage_num:02d}_{desc['slug']}.png",
                "url": f"/api/jobs/{self.job_id}/stages/stage_{stage_num:02d}.png",
                "generated": exists,
            })

        val_summary = {
            "overall_score": validation.get("overall_score", 95.0) if validation else None,
            "status": validation.get("status", "PASS") if validation else "NOT_RUN",
            "warnings_count": len(validation.get("warnings", [])) if validation else 0,
        }

        manifest = {
            "schema_version": "1.0",
            "job_id": self.job_id,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "elapsed_seconds": round(elapsed_seconds, 2),
            "source_image": {
                "filename": source_image_name,
                "width": image_meta.get("width", 0),
                "height": image_meta.get("height", 0),
                "url": f"/api/jobs/{self.job_id}/original",
            },
            "pose": {
                "yaw": round(float(pose.get("yaw", 0.0)), 1),
                "pitch": round(float(pose.get("pitch", 0.0)), 1),
                "roll": round(float(pose.get("roll", 0.0)), 1),
                "orientation": pose.get("orientation", "unknown"),
            },
            "analysis_status": "SUCCESS" if analysis.get("success") else "FAILED",
            "construction_schema_version": construction.get("version", "4.0"),
            "validation_summary": val_summary,
            "stages_count": len(stages_list),
            "stages": stages_list,
            "archive_url": f"/api/jobs/{self.job_id}/download-zip",
            "final_portrait_url": f"/api/jobs/{self.job_id}/stages/stage_20.png",
        }

        manifest_file = self.job_dir / "manifest.json"
        with open(manifest_file, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return manifest

    def create_zip_archive(self) -> Path:
        """Create a complete ZIP archive containing all stages, original, and metadata."""
        zip_path = self.job_dir / f"loomis_drawing_{self.job_id}.zip"
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for f in self.job_dir.iterdir():
                if f.is_file() and f.suffix.lower() != ".zip":
                    zf.write(f, arcname=f.name)
            if self.stages_dir.exists():
                for f in self.stages_dir.iterdir():
                    if f.is_file():
                        zf.write(f, arcname=f"stages/{f.name}")
        return zip_path
