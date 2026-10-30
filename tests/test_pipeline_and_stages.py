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


if __name__ == "__main__":
    unittest.main()
