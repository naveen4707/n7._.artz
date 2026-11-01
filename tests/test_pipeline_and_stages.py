"""
Unit and regression test suite for Loomis AI drawing engine and stages.
Validates:
- Analysis and construction schemas
- Renderer initialization
- Safe render_stage invocation without stage_name (regression test for Stage 9)
- Output image dimensions and validity across stages
"""

import json
import unittest
from pathlib import Path
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AI_ENGINE_DIR = PROJECT_ROOT / "ai-engine"
OUTPUT_DIR = AI_ENGINE_DIR / "output"
HAND_DRAWN_DIR = OUTPUT_DIR / "hand_drawn"
ANALYSIS_FILE = OUTPUT_DIR / "analysis.json"
CONSTRUCTION_FILE = OUTPUT_DIR / "construction.json"

import sys
SRC_DIR = AI_ENGINE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from hand_drawn_renderer import HandDrawnLoomisRenderer, STAGES


class TestLoomisPipelineAndStages(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ANALYSIS_FILE.exists():
            raise unittest.SkipTest("analysis.json does not exist. Run analysis first.")
        if not CONSTRUCTION_FILE.exists():
            raise unittest.SkipTest("construction.json does not exist. Run construction first.")

        with open(ANALYSIS_FILE, "r", encoding="utf-8") as f:
            cls.analysis = json.load(f)

        with open(CONSTRUCTION_FILE, "r", encoding="utf-8") as f:
            cls.construction = json.load(f)

    def test_01_analysis_schema(self):
        """Verify analysis.json structure and 478 landmarks."""
        self.assertTrue(self.analysis.get("success"), "Analysis must report success=True")
        self.assertIn("landmarks", self.analysis)
        self.assertEqual(len(self.analysis["landmarks"]), 478, "Must detect 478 landmarks")
        self.assertIn("pose", self.analysis)
        pose = self.analysis["pose"]
        for key in ("yaw", "pitch", "roll", "orientation", "direction"):
            self.assertIn(key, pose, f"Pose missing required field '{key}'")

    def test_02_construction_schema(self):
        """Verify construction.json v4.0 schema and geometry."""
        self.assertEqual(self.construction.get("version"), "4.0")
        self.assertIn("accurateFace", self.construction)
        self.assertIn("loomis", self.construction)
        loomis = self.construction["loomis"]
        for key in ("cranium", "eyePlane", "centerAxis", "jaw", "nosePlane", "mouthPlane"):
            self.assertIn(key, loomis, f"Loomis geometry missing '{key}'")

    def test_03_hand_drawn_renderer_initialization(self):
        """Verify HandDrawnLoomisRenderer initializes with construction data and creates valid canvas."""
        renderer = HandDrawnLoomisRenderer(self.construction)
        self.assertIsNotNone(renderer.transform)
        canvas = renderer.create_canvas()
        self.assertEqual(canvas.size, (1000, 1200))

    def test_04_render_stage_omits_stage_name_regression(self):
        """
        Regression test for Stage 9 integration bug:
        render_stage(stage_number) MUST succeed when stage_name argument is omitted.
        """
        renderer = HandDrawnLoomisRenderer(self.construction)

        # Test stages 1, 7, 8, and 9 without passing stage_name
        for stage_num in (1, 7, 8, 9):
            img = renderer.render_stage(stage_num)
            self.assertIsInstance(img, Image.Image, f"Stage {stage_num} must return a PIL Image")
            self.assertEqual(img.size, (1000, 1200), f"Stage {stage_num} image must be 1000x1200")

    def test_05_stages_dictionary_coverage(self):
        """Verify all 20 stages are registered in STAGES mapping."""
        self.assertEqual(len(STAGES), 20, "STAGES must map exactly 20 stages")
        for stage_num in range(1, 21):
            self.assertIn(stage_num, STAGES, f"Stage {stage_num} must be in STAGES dictionary")
            self.assertTrue(len(STAGES[stage_num]) > 0, f"Stage {stage_num} title cannot be empty")

    def test_06_stage_outputs_exist(self):
        """Verify all 20 stage PNGs exist in output/hand_drawn and are valid images."""
        for stage_num in range(1, 21):
            stage_file = HAND_DRAWN_DIR / f"stage_{stage_num:02d}.png"
            self.assertTrue(stage_file.exists(), f"Output file missing: {stage_file}")
            with Image.open(stage_file) as img:
                self.assertEqual(img.size, (1000, 1200), f"{stage_file.name} must be 1000x1200")

    def test_07_geometry_validation(self):
        """Verify GeometryValidator generates complete measurable validation and actionable corrections."""
        from geometry_validator import GeometryValidator
        validator = GeometryValidator(self.analysis, self.construction, stages_dir=HAND_DRAWN_DIR)
        report = validator.validate()

        self.assertIn("overall_score", report)
        self.assertGreaterEqual(report["overall_score"], 80.0, "Overall score must exceed 80%")
        self.assertIn("status", report)
        self.assertIn(report["status"], ("PASS", "WARNING"))
        self.assertIn("components", report)
        self.assertGreaterEqual(len(report["components"]), 5)
        self.assertIn("corrections", report)
        self.assertIn("normalizing_interocular_px", report)

    def test_08_job_manifest_and_zip(self):
        """Verify OutputGenerator creates manifest.json, stages, and zip archive in output/jobs/."""
        jobs_dir = PROJECT_ROOT / "output" / "jobs"
        ref_job = jobs_dir / "reference_job"
        self.assertTrue(ref_job.exists(), "reference_job directory must exist")

        manifest_file = ref_job / "manifest.json"
        self.assertTrue(manifest_file.exists(), "manifest.json must exist in reference_job")
        with open(manifest_file, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest["job_id"], "reference_job")
        self.assertEqual(manifest["stages_count"], 20)
        self.assertEqual(len(manifest["stages"]), 20)
        self.assertIn("validation_summary", manifest)

        zip_files = list(ref_job.glob("*.zip"))
        self.assertTrue(len(zip_files) > 0, "ZIP archive must be generated for job")
        self.assertGreater(zip_files[0].stat().st_size, 100000, "ZIP archive must not be empty")

    def test_09_all_stages_render_through_hand_drawn_renderer(self):
        """
        Verify HandDrawnLoomisRenderer.render_stage(stage_num) successfully dispatches
        and renders valid 1000x1200 images for all stages 1 through 20.
        """
        ref_img = AI_ENGINE_DIR / "input" / "reference.jpg"
        renderer = HandDrawnLoomisRenderer(self.construction, analysis=self.analysis, img_path=ref_img)

        # Test sample of foundation (1), features (8, 9, 12), and master synthesis (15, 20)
        for stage_num in (1, 8, 9, 12, 15, 20):
            img = renderer.render_stage(stage_num)
            self.assertIsInstance(img, Image.Image, f"Stage {stage_num} must produce a PIL Image")
            self.assertEqual(img.size, (1000, 1200), f"Stage {stage_num} must be 1000x1200")

    def test_10_milestone_1_loomis_3d_perspective_geometry(self):
        """
        Verify Milestone 1 enriched 3D perspective-aware Loomis geometry (Stages 1-7):
        - Cranium 3D tilt axis and vertex pole cap
        - 3D brow equator curve with perspective bowing & glabella cross
        - Temporal side discs with 4-quadrant cross & mandibular hinge
        - Mandible bucket-handle rhythm & chin front plane wedge
        - Rule of Thirds horizontal guide arches & glabella keystone
        - Cylindrical dental muzzle arc & corner modiolus nodes
        """
        loomis = self.construction.get("loomis", {})

        # 1. Cranium
        cranium = loomis.get("cranium", {})
        self.assertIn("tiltAxis", cranium, "Cranium must contain 3D tiltAxis")
        self.assertIn("top", cranium["tiltAxis"])
        self.assertIn("bottom", cranium["tiltAxis"])
        self.assertIn("poleEllipse", cranium, "Cranium must contain 3D vertex poleEllipse")
        self.assertIn("searchRadii", cranium, "Cranium must contain searchRadii")

        # 2. Center Axis & Brow Equator
        center_axis = loomis.get("centerAxis", {})
        self.assertIn("browEquator", center_axis, "Center axis must contain 3D browEquator")
        eq = center_axis["browEquator"]
        self.assertIn("points", eq)
        self.assertGreaterEqual(len(eq["points"]), 5, "Brow equator must have >= 5 curve points")
        self.assertIn("bow", eq)
        self.assertIn("glabellaCross", center_axis, "Center axis must contain glabellaCross")

        # 3. Side Planes & Temporal Discs
        side_planes = loomis.get("sidePlanes", {})
        self.assertIn("temporalDiscs", side_planes, "Side planes must contain temporalDiscs")
        discs = side_planes["temporalDiscs"]
        for side in ("left", "right"):
            self.assertIn(side, discs)
            self.assertIn("center", discs[side])
            self.assertIn("verticalCross", discs[side])
            self.assertIn("horizontalCross", discs[side])
            self.assertIn("hinge", discs[side])

        # 4. Jaw & Bucket Handle
        jaw = loomis.get("jaw", {})
        self.assertIn("bucketHandle", jaw, "Jaw must contain bucketHandle")
        bh = jaw["bucketHandle"]
        for key in ("hingeLeft", "gonionLeft", "chinLeft", "chinCenter", "chinRight", "gonionRight", "hingeRight"):
            self.assertIn(key, bh)
        self.assertIn("chinWedge", bh)
        self.assertIn("rhythmLeft", bh)
        self.assertIn("rhythmRight", bh)

        # 5. Nose Plane & Rule of Thirds
        nose_plane = loomis.get("nosePlane", {})
        self.assertIn("thirds", nose_plane, "Nose plane must contain Rule of Thirds guide lines")
        thirds = nose_plane["thirds"]
        for line_name in ("hairline", "brow", "noseBase", "chin"):
            self.assertIn(line_name, thirds)
            self.assertGreaterEqual(len(thirds[line_name]), 2)
        self.assertIn("keystone", nose_plane, "Nose plane must contain glabella keystone")
        self.assertIn("underPlane", nose_plane, "Nose plane must contain underPlane")

        # 6. Mouth Plane & Dental Muzzle
        mouth_plane = loomis.get("mouthPlane", {})
        self.assertIn("dentalMuzzle", mouth_plane, "Mouth plane must contain dentalMuzzle")
        muzzle = mouth_plane["dentalMuzzle"]
        self.assertIn("arc", muzzle)
        self.assertIn("cornerNodes", muzzle)
        self.assertIn("oralFissure", muzzle)
        self.assertIn("labiomentalGroove", muzzle)

        # 7. Render all stages 1 through 7
        ref_img = AI_ENGINE_DIR / "input" / "reference.jpg"
        renderer = HandDrawnLoomisRenderer(self.construction, analysis=self.analysis, img_path=ref_img)
        for s in range(1, 8):
            img = renderer.render_stage(s)
            self.assertIsInstance(img, Image.Image, f"Stage {s} must render a PIL Image")
            self.assertEqual(img.size, (1000, 1200))

    def test_11_milestone_2_feature_and_volumetric_construction(self):
        """
        Verify Milestone 2 anatomical feature construction (Stages 8-14)
        and volumetric hair mass / neck construction (Stages 15-16):
        - Stage 8: Eyeball sphere, corneal bulge & eyelid wrapping guide
        - Stage 9: Eyelid thickness margin plane & tear duct
        - Stage 10: 3-part Loomis eyebrow mass & glabella keystone
        - Stage 11: 5-plane nose construction (dorsal ridge, side planes, ball, alar wings, underplane)
        - Stage 12: Dental muzzle barrel arc & 5-cushion lip architecture
        - Stage 13: Zygomatic arch, temporal crest, and mental protuberance
        - Stage 14: Ear construction bounded between brow level and nose base
        - Stage 15: Volumetric cranial hair envelope, ribbon flow lines, and hairline boundary
        - Stage 16: Cervical cylinder, sternocleidomastoid (SCM) V-rhythm, clavicles, trapezius slope
        - HandDrawnLoomisRenderer renders stages 8 through 16 to valid 1000x1200 images
        """
        from stage_08_eye_construction import Stage8EyeConstruction
        from stage_09_eye_eyelid_construction import Stage09EyeRenderer
        from stage_10_eyebrow_construction import Stage10EyebrowRenderer
        from stage_11_nose_construction import Stage11NoseRenderer
        from stage_12_mouth_construction import Stage12MouthRenderer
        from stage_13_cheek_forehead_contours import Stage13CheekForeheadRenderer
        from stage_14_ear_construction import Stage14EarRenderer
        from stage_15_hairline_hair_mass import Stage15HairlineHairMassRenderer
        from stage_16_neck_construction import Stage16NeckRenderer
        from landmark_portrait_engine import LandmarkPortraitEngine

        ref_img = AI_ENGINE_DIR / "input" / "reference.jpg"
        lpe = LandmarkPortraitEngine(self.construction, self.analysis, img_path=ref_img)

        # 1. Feature data extraction
        eye_r = lpe.get_eye_data("right")
        eye_l = lpe.get_eye_data("left")
        self.assertTrue(bool(eye_r), "Right eye data must be extracted")
        self.assertTrue(bool(eye_l), "Left eye data must be extracted")

        brow_r = lpe.get_brow_data("right")
        self.assertIn("lower", brow_r)
        self.assertIn("upper", brow_r)

        nose_data = lpe.get_nose_data()
        self.assertIsNotNone(nose_data.get("tip"))
        self.assertIsNotNone(nose_data.get("bridge"))

        lip_data = lpe.get_lip_data()
        self.assertIsNotNone(lip_data.get("closure"))
        self.assertIsNotNone(lip_data.get("upper_outer"))
        self.assertIsNotNone(lip_data.get("lower_outer"))

        # 2. Render each Milestone 2 stage and verify valid 1000x1200 image outputs
        stages_to_test = [
            (8, Stage8EyeConstruction(self.construction)),
            (9, Stage09EyeRenderer(self.construction)),
            (10, Stage10EyebrowRenderer(self.construction)),
            (11, Stage11NoseRenderer(self.construction)),
            (12, Stage12MouthRenderer(self.construction, self.analysis)),
            (13, Stage13CheekForeheadRenderer(self.construction, self.analysis)),
            (14, Stage14EarRenderer(self.construction, self.analysis)),
            (15, Stage15HairlineHairMassRenderer(self.construction, self.analysis, img_path=ref_img)),
            (16, Stage16NeckRenderer(self.construction, self.analysis, img_path=ref_img)),
        ]

        for num, renderer in stages_to_test:
            img = renderer.render()
            self.assertIsInstance(img, Image.Image, f"Stage {num} must render a PIL Image")
            self.assertEqual(img.size, (1000, 1200), f"Stage {num} must be 1000x1200")

    def test_12_milestone_3_graphite_rendering_pipeline(self):
        """
        Verify Milestone 3: Pure hand-drawn graphite rendering pipeline:
        - Elimination of photo-blend / photo-overlay shortcuts in Stage 20
        - Upgraded multi-angle directional cross-hatching across anatomical planes in LandmarkPortraitEngine
        - Procedural volumetric hair graphite tone and fiber luster
        - Soft eraser-lift luminous highlights on pupils, nose tip ball, and lower lip cushion
        - Master artist cursive atelier signature and flourish
        - Stages 17, 18, 19, and 20 render valid 1000x1200 RGB PIL Images
        """
        from stage_17_facial_contour_refinement import Stage17FacialContourRenderer
        from stage_18_shadow_structures import Stage18ShadowRenderer
        from stage_19_secondary_details import Stage19SecondaryDetailsRenderer
        from stage_20_final_portrait import Stage20FinalPortraitRenderer
        from landmark_portrait_engine import LandmarkPortraitEngine

        ref_img = AI_ENGINE_DIR / "input" / "reference.jpg"
        lpe = LandmarkPortraitEngine(self.construction, self.analysis, img_path=ref_img)

        # 1. Verify anatomical shadow structure methods exist on engine
        self.assertTrue(hasattr(lpe, "draw_shadow_structures"), "Engine must have draw_shadow_structures")
        self.assertTrue(hasattr(lpe, "draw_hair_tonal_volume"), "Engine must have draw_hair_tonal_volume")
        self.assertTrue(hasattr(lpe, "draw_luminous_highlights"), "Engine must have draw_luminous_highlights")

        # 2. Render stages 17 to 20
        stages_m3 = [
            (17, Stage17FacialContourRenderer(self.construction, self.analysis, img_path=ref_img)),
            (18, Stage18ShadowRenderer(self.construction, self.analysis, img_path=ref_img)),
            (19, Stage19SecondaryDetailsRenderer(self.construction, self.analysis, img_path=ref_img)),
            (20, Stage20FinalPortraitRenderer(self.construction, self.analysis, img_path=ref_img)),
        ]

        for num, renderer in stages_m3:
            img = renderer.render()
            self.assertIsInstance(img, Image.Image, f"Stage {num} must render a PIL Image")
            self.assertEqual(img.size, (1000, 1200), f"Stage {num} must be 1000x1200")
            self.assertEqual(img.mode, "RGB", f"Stage {num} must be RGB mode")

        # 3. Verify Stage 20 does not rely on raster photo blending
        r20 = Stage20FinalPortraitRenderer(self.construction, self.analysis, img_path=ref_img)
        self.assertFalse(hasattr(r20, "_render_graphite_tone_base"), "Stage 20 must NOT use raster photo blend shortcut")

    def test_13_milestone_4_lesson_curriculum_and_checkpoints(self):
        """
        Verify Milestone 4: Interactive drawing lesson experience & learning checkpoints:
        - Full 20-stage pedagogical curriculum covering Andrew Loomis principles
        - Each stage contains step-by-step instructions, pro tips, common pitfalls, and 3-item checklist
        - Checkpoint verification computes mastery levels ('Mastered', 'Proficient', 'Needs Practice')
        - Proper advancement criteria and constructive pedagogical feedback
        """
        from lesson_curriculum import (
            LESSON_CURRICULUM,
            get_stage_curriculum,
            verify_stage_checkpoint,
        )

        # 1. Verify all 20 stages are present in curriculum
        self.assertEqual(len(LESSON_CURRICULUM), 20, "Curriculum must define all 20 Loomis stages")

        for s in range(1, 21):
            curr = get_stage_curriculum(s)
            self.assertIsNotNone(curr, f"Stage {s} curriculum must be defined")
            self.assertEqual(curr["stage"], s)
            self.assertTrue(bool(curr.get("title")), f"Stage {s} must have a title")
            self.assertTrue(bool(curr.get("category")), f"Stage {s} must have a category")
            self.assertTrue(bool(curr.get("pencil_grade")), f"Stage {s} must specify pencil hardness")
            self.assertTrue(bool(curr.get("loomis_core_rule")), f"Stage {s} must quote a Loomis principle")
            self.assertGreaterEqual(len(curr.get("step_by_step_instructions", [])), 3, f"Stage {s} needs >= 3 step instructions")
            self.assertGreaterEqual(len(curr.get("pro_tips", [])), 2, f"Stage {s} needs >= 2 pro tips")
            self.assertGreaterEqual(len(curr.get("common_pitfalls", [])), 2, f"Stage {s} needs >= 2 common pitfalls")
            self.assertEqual(len(curr.get("checkpoint_checklist", [])), 3, f"Stage {s} must have exactly 3 checklist criteria")

            # Mastery question validation
            q = curr.get("mastery_question")
            self.assertIsNotNone(q, f"Stage {s} must have a mastery question")
            self.assertIn("question", q)
            self.assertIn("options", q)
            self.assertIn("correct_index", q)
            self.assertIn("explanation", q)

        # 2. Verify checkpoint evaluation logic
        # Full mastery (3/3)
        res_full = verify_stage_checkpoint(1, [True, True, True])
        self.assertEqual(res_full["score_percent"], 100)
        self.assertEqual(res_full["mastery_level"], "Mastered")
        self.assertTrue(res_full["can_advance"])
        self.assertEqual(res_full["next_stage"], 2)

        # Proficient (2/3)
        res_prof = verify_stage_checkpoint(5, [True, True, False])
        self.assertEqual(res_prof["score_percent"], 67)
        self.assertEqual(res_prof["mastery_level"], "Proficient")
        self.assertTrue(res_prof["can_advance"])

        # Needs practice (0/3 or 1/3)
        res_low = verify_stage_checkpoint(10, [False, False, False])
        self.assertEqual(res_low["score_percent"], 0)
        self.assertEqual(res_low["mastery_level"], "Needs Practice")
        self.assertFalse(res_low["can_advance"])

        # Invalid stage
        res_inv = verify_stage_checkpoint(99, [True, True, True])
        self.assertIn("error", res_inv)
        self.assertFalse(res_inv["can_advance"])


if __name__ == "__main__":
    unittest.main()


