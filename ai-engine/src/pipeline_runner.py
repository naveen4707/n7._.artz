"""
LOOMIS AI — UNIFIED 20-STAGE PIPELINE RUNNER
Automates the full 20-stage Loomis portrait construction pipeline for ANY uploaded photo:
1. MediaPipe 478 Landmark & Head Pose Analysis (Member 1)
2. Loomis Head Geometry Generation (Member 2 Construction)
3. Stages 1–7: Loomis Cranial Armature (Hand-Drawn Graphite)
4. Stages 8–14: Anatomical Feature Construction (Eyes, Brows, Nose, Mouth, Cheeks, Ears)
5. Stages 15–20: Dynamic Photo-Accurate Outlines (Hair, Neck, Dress, Shadows, Secondary Details, Final Masterpiece)
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = AI_ENGINE_DIR / "src"
INPUT_DIR = AI_ENGINE_DIR / "input"
OUTPUT_DIR = AI_ENGINE_DIR / "output"
HAND_DRAWN_DIR = OUTPUT_DIR / "hand_drawn"
MODELS_DIR = AI_ENGINE_DIR / "models"


class LoomisPipeline:
    """Executes the complete 20-stage Loomis portrait generation pipeline."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
    ) -> None:
        self.output_dir = Path(output_dir) if output_dir else HAND_DRAWN_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def process(
        self,
        image_path: Path | str,
        stages_to_run: Optional[List[int]] = None,
        progress_callback: Optional[Any] = None,
        job_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        t0 = time.time()
        img_p = Path(image_path)
        if not img_p.is_absolute():
            cwd_cand = (Path.cwd() / img_p).resolve()
            engine_cand = (AI_ENGINE_DIR / img_p).resolve()
            if cwd_cand.exists():
                img_p = cwd_cand
            elif engine_cand.exists():
                img_p = engine_cand
            else:
                img_p = cwd_cand
        if not img_p.exists():
            raise FileNotFoundError(f"Input image not found: {img_p}")

        if stages_to_run is None:
            stages_to_run = list(range(1, 21))

        effective_job_id = job_id or f"job_{int(t0)}"

        print("=" * 60)
        print("          LOOMIS AI — FULL 20-STAGE PIPELINE")
        print("=" * 60)
        print(f"Input portrait: {img_p.name}")
        print(f"Job identifier: {effective_job_id}")
        print(f"Output folder:  {self.output_dir}")
        print()

        # ── STEP 0: BLACK & WHITE CONVERSION ─────────────────────────
        if progress_callback:
            progress_callback(2, "Converting portrait into studio Black & White tonal reference...")
        print("[0/4] Converting portrait into high-contrast Black & White reference picture...")

        from bw_converter import convert_to_black_and_white
        bw_path = self.output_dir / "bw_reference.jpg"
        try:
            convert_to_black_and_white(img_p, bw_path)
            print(f"  [OK] Black & White reference generated: {bw_path.name}")
        except Exception as e:
            print(f"  [WARN] B&W conversion note: {e}")
            bw_path = img_p

        # ── STEP 1: VISUAL ANALYSIS ─────────────────────────────────
        if progress_callback:
            progress_callback(5, "Analyzing facial landmarks and head pose...")
        print("[1/4] Running MediaPipe Face Landmarker & Pose Estimator...")

        from config import (
            FACE_LANDMARKER_MODEL,
            MIN_FACE_DETECTION_CONFIDENCE,
            MIN_FACE_PRESENCE_CONFIDENCE,
            MIN_TRACKING_CONFIDENCE,
            NUM_FACES,
            validate_project,
        )
        from face_analyzer import FaceAnalyzer
        from landmark_analyzer import LandmarkAnalyzer
        from pose_estimator import PoseEstimator

        validate_project()
        landmark_analyzer = LandmarkAnalyzer(
            model_path=FACE_LANDMARKER_MODEL,
            num_faces=NUM_FACES,
            min_face_detection_confidence=MIN_FACE_DETECTION_CONFIDENCE,
            min_face_presence_confidence=MIN_FACE_PRESENCE_CONFIDENCE,
            min_tracking_confidence=MIN_TRACKING_CONFIDENCE,
        )
        pose_estimator = PoseEstimator()
        analyzer = FaceAnalyzer(landmark_analyzer, pose_estimator)

        try:
            analysis = analyzer.analyze(img_p)
        finally:
            analyzer.close()

        if not analysis.get("success"):
            raise RuntimeError(f"Face analysis failed: {analysis.get('error')}")

        analysis_file = OUTPUT_DIR / "analysis.json"
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Analysis complete: {len(analysis.get('landmarks', []))} landmarks detected")

        # ── STEP 2: LOOMIS GEOMETRY ─────────────────────────────────
        if progress_callback:
            progress_callback(5, "Generating Loomis cranial geometry...")
        print("[2/3] Generating 3D Loomis construction geometry...")

        from loomis_geometry import LoomisGeometry

        geometry = LoomisGeometry(analysis)
        construction = geometry.build()

        construction_file = OUTPUT_DIR / "construction.json"
        with open(construction_file, "w", encoding="utf-8") as f:
            json.dump(construction, f, indent=2, ensure_ascii=False)
        print("  [OK] Construction geometry generated successfully")

        # ── STEP 3: RENDER STAGES 1 TO 20 ───────────────────────────
        print("[3/3] Rendering 20 graphite drawing stages...")

        from hand_drawn_renderer import STAGES as STAGES_7, HandDrawnLoomisRenderer
        from landmark_portrait_engine import LandmarkPortraitEngine

        lpe = LandmarkPortraitEngine(construction, analysis, img_path=img_p)
        hdr = HandDrawnLoomisRenderer(construction, analysis=analysis, img_path=img_p)

        rendered_files: Dict[int, Path] = {}

        # Stage 1 to 7: Loomis Foundation
        for stage_num in range(1, 8):
            if stage_num not in stages_to_run:
                continue
            stage_name = STAGES_7.get(stage_num, f"Stage {stage_num}")
            if progress_callback:
                progress_callback(stage_num * 4, f"Rendering Stage {stage_num:02d}: {stage_name}")

            out_file = self.output_dir / f"stage_{stage_num:02d}.png"
            img = hdr.render_stage(stage_num, stage_name)
            img.save(out_file, quality=95)
            rendered_files[stage_num] = out_file
            print(f"  [OK] Stage {stage_num:02d}: {stage_name}")

        # Stage 8 to 14: Facial Feature Construction
        from stage_08_eye_construction import Stage8EyeConstruction
        from stage_09_eye_eyelid_construction import Stage09EyeRenderer
        from stage_10_eyebrow_construction import Stage10EyebrowRenderer
        from stage_11_nose_construction import Stage11NoseRenderer
        from stage_12_mouth_construction import Stage12MouthRenderer
        from stage_13_cheek_forehead_contours import Stage13CheekForeheadRenderer
        from stage_14_ear_construction import Stage14EarRenderer

        def _render_stage_8_14(num: int, out_p: Path) -> None:
            if num == 8:
                img = Stage8EyeConstruction(construction).render()
                img.save(out_p, quality=95)
            elif num == 9:
                Stage09EyeRenderer(construction).save(out_p)
            elif num == 10:
                Stage10EyebrowRenderer(construction).save(out_p)
            elif num == 11:
                Stage11NoseRenderer(construction).save(out_p)
            elif num == 12:
                Stage12MouthRenderer(construction, analysis).save(out_p)
            elif num == 13:
                Stage13CheekForeheadRenderer(construction, analysis).save(out_p)
            elif num == 14:
                Stage14EarRenderer(construction, analysis).save(out_p)

        names_8_14 = {
            8: "Eye Construction",
            9: "Eye and Eyelid Construction",
            10: "Eyebrow Construction",
            11: "Nose Construction",
            12: "Mouth Construction",
            13: "Cheek and Forehead Contours",
            14: "Ear Construction",
        }

        for stage_num, name in names_8_14.items():
            if stage_num not in stages_to_run:
                continue
            if progress_callback:
                progress_callback(32 + (stage_num - 8) * 5, f"Rendering Stage {stage_num:02d}: {name}")
            out_file = self.output_dir / f"stage_{stage_num:02d}.png"
            _render_stage_8_14(stage_num, out_file)
            rendered_files[stage_num] = out_file
            print(f"  [OK] Stage {stage_num:02d}: {name}")

        # Stage 15 to 20: Photo-Accurate Outlines, Shadows & Masterpiece
        from stage_15_hairline_hair_mass import Stage15HairlineHairMassRenderer
        from stage_16_neck_construction import Stage16NeckRenderer
        from stage_17_facial_contour_refinement import Stage17FacialContourRenderer
        from stage_18_shadow_structures import Stage18ShadowRenderer
        from stage_19_secondary_details import Stage19SecondaryDetailsRenderer
        from stage_20_final_portrait import Stage20FinalPortraitRenderer

        stage_renderers_15_20 = {
            15: (Stage15HairlineHairMassRenderer, "Hairline and Hair Mass"),
            16: (Stage16NeckRenderer, "Neck and Shoulders Construction"),
            17: (Stage17FacialContourRenderer, "Facial Contour Refinement"),
            18: (Stage18ShadowRenderer, "Major Shadow Structures"),
            19: (Stage19SecondaryDetailsRenderer, "Secondary Details"),
            20: (Stage20FinalPortraitRenderer, "Final Master Graphite Portrait"),
        }

        for stage_num, (cls, name) in stage_renderers_15_20.items():
            if stage_num not in stages_to_run:
                continue
            if progress_callback:
                progress_callback(70 + (stage_num - 15) * 5, f"Rendering Stage {stage_num:02d}: {name}")
            out_file = self.output_dir / f"stage_{stage_num:02d}.png"
            r = cls(construction, analysis, img_path=img_p)
            r.save(out_file)
            rendered_files[stage_num] = out_file
            print(f"  [OK] Stage {stage_num:02d}: {name}")

        # ── STEP 4: GEOMETRY VALIDATION & MEASURABLE CORRECTION ─────
        if progress_callback:
            progress_callback(95, "Running measurable geometry validation...")
        print("[4/4] Validating Loomis geometry and computing actionable corrections...")

        from geometry_validator import GeometryValidator
        validator = GeometryValidator(analysis, construction, stages_dir=self.output_dir)
        validation_report = validator.validate()

        validation_file = OUTPUT_DIR / "validation.json"
        with open(validation_file, "w", encoding="utf-8") as f:
            json.dump(validation_report, f, indent=2, ensure_ascii=False)
        print(f"  [OK] Validation report: score {validation_report['overall_score']}% ({validation_report['status']})")

        # ── STEP 5: OUTPUT GENERATOR & MANIFEST ───────────────────────
        from output_generator import OutputGenerator
        og = OutputGenerator(job_id=effective_job_id)
        og.save_source_image(img_p)
        if bw_path.exists():
            og.save_bw_image(bw_path)
        og.save_analysis(analysis)
        og.save_construction(construction)
        og.save_validation(validation_report)
        for s_num, s_path in rendered_files.items():
            og.record_stage_image(s_num, s_path)

        elapsed = time.time() - t0
        manifest = og.generate_manifest(
            analysis=analysis,
            construction=construction,
            validation=validation_report,
            source_image_name=img_p.name,
            elapsed_seconds=elapsed,
        )
        og.create_zip_archive()
        print(f"  [OK] Manifest and job package created: output/jobs/{effective_job_id}/")

        print()
        print("=" * 60)
        print(f"  ALL 20 STAGES COMPLETE in {elapsed:.2f} seconds!")
        print("=" * 60)

        if progress_callback:
            progress_callback(100, f"Complete! 20 stages generated in {elapsed:.1f}s")

        return {
            "success": True,
            "elapsed_seconds": elapsed,
            "job_id": effective_job_id,
            "bw_image_path": str(bw_path),
            "image": analysis.get("image", {}),
            "pose": analysis.get("pose", {}),
            "stages": {k: str(v) for k, v in rendered_files.items()},
            "validation": validation_report,
            "manifest": manifest,
        }


def main():
    parser = argparse.ArgumentParser(description="Loomis AI - Universal 20-Stage Pipeline Runner")
    parser.add_argument("--input", default="input/reference.jpg", help="Path to input portrait photo")
    parser.add_argument("--output-dir", default=str(HAND_DRAWN_DIR), help="Directory to save stage drawings")
    parser.add_argument("--stages", type=int, nargs="*", default=None, help="Optional specific stages to render")
    parser.add_argument("--job-id", default=None, help="Optional job identifier for isolated output directory")
    args = parser.parse_args()

    pipeline = LoomisPipeline(output_dir=Path(args.output_dir))
    pipeline.process(image_path=args.input, stages_to_run=args.stages, job_id=args.job_id)


if __name__ == "__main__":
    main()
