from pathlib import Path


# ---------------------------------------------------------
# LOOMIS AI - PROJECT CONFIGURATION
# ---------------------------------------------------------

AI_ENGINE_DIR = Path(__file__).resolve().parent.parent

MODELS_DIR = AI_ENGINE_DIR / "models"
INPUT_DIR = AI_ENGINE_DIR / "input"
OUTPUT_DIR = AI_ENGINE_DIR / "output"

FACE_LANDMARKER_MODEL = MODELS_DIR / "face_landmarker.task"

DEFAULT_OUTPUT_FILE = OUTPUT_DIR / "analysis.json"


# MediaPipe configuration
NUM_FACES = 1

MIN_FACE_DETECTION_CONFIDENCE = 0.5
MIN_FACE_PRESENCE_CONFIDENCE = 0.5
MIN_TRACKING_CONFIDENCE = 0.5


# ---------------------------------------------------------
# Validate required project resources
# ---------------------------------------------------------

def validate_project():
    """
    Checks that the required directories and MediaPipe
    model exist before the AI pipeline starts.
    """

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not FACE_LANDMARKER_MODEL.exists():
        raise FileNotFoundError(
            f"Face Landmarker model not found:\n"
            f"{FACE_LANDMARKER_MODEL}"
        )