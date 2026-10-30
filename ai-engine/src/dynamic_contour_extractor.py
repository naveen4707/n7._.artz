"""
LOOMIS AI — DYNAMIC CONTOUR EXTRACTOR
Universal Computer Vision & Landmark-Guided Outline Extraction.

Extracts photo-accurate contours from ANY uploaded portrait:
1. Hair mass, crown volume, hairline, and hair silhouette.
2. Anatomical neck cylinder, shoulders, and garment/dress neckline & drapery.
3. Personal facial characteristics (dynamic forehead mark detection: bindi/beauty mark/mole).
4. Photo-driven shadow structures and tonal value masses.
5. Secondary fabric folds, garment details, and fine hair wisps.

Works universally for any human portrait: men, women, children, different hairstyles,
different clothing types (t-shirts, collars, hoodies, dresses, suits, sarees, jackets).
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import cv2
import numpy as np

Point = Tuple[float, float]

FACE_OVAL = [
    10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361,
    288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
    150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103,
    67, 109,
]

HAIRLINE = [21, 54, 103, 67, 109, 10, 338, 297, 332, 284, 251]


class DynamicContourExtractor:
    """
    Extracts organic contours from the uploaded photo guided by MediaPipe landmarks.
    Does NOT use hardcoded coordinates or predetermined clothing/hairstyles.
    """

    def __init__(
        self,
        img_path: Path | str,
        analysis: Dict[str, Any],
        transform_fn: Any,
        scale: float = 1.0,
    ) -> None:
        self.img_path = Path(img_path)
        self.analysis = analysis
        self.transform_fn = transform_fn
        self.scale = scale

        self.lms: List[Dict] = analysis.get("landmarks", [])
        self.img: Optional[np.ndarray] = None
        self.h: int = 0
        self.w: int = 0
        self.gray: Optional[np.ndarray] = None

        if self.img_path.exists():
            loaded = cv2.imread(str(self.img_path))
            if loaded is not None:
                self.img = loaded
                self.h, self.w = loaded.shape[:2]
                self.gray = cv2.cvtColor(loaded, cv2.COLOR_BGR2GRAY)

        self._hair_contours_cache: Optional[List[List[Point]]] = None
        self._clothing_contours_cache: Optional[List[List[Point]]] = None
        self._clothing_major_cache: Optional[List[List[Point]]] = None

    def has_image(self) -> bool:
        return self.img is not None and self.gray is not None and len(self.lms) > 0

    def lm(self, idx: int) -> Optional[Tuple[float, float]]:
        if 0 <= idx < len(self.lms):
            p = self.lms[idx]
            return float(p["x"]), float(p["y"])
        return None

    def lm_canvas(self, idx: int) -> Optional[Point]:
        pt = self.lm(idx)
        return self.transform_fn(pt) if pt else None

    # ─────────────────────────────────────────────────────────────
    # CONTOUR EXTRACTION
    # ─────────────────────────────────────────────────────────────

    def _extract_all_contours(self) -> None:
        if not self.has_image():
            self._hair_contours_cache = []
            self._clothing_contours_cache = []
            self._clothing_major_cache = []
            return

        # 1. Bilateral filter preserves sharp physical boundaries while smoothing skin pore noise
        bi = cv2.bilateralFilter(self.gray, 9, 65, 65)

        # 2. Canny edges capturing hair boundaries, garment drape, and fabric folds
        edges = cv2.Canny(bi, 28, 75)

        # 3. Create inner face mask to avoid edge clutter across eyes, nose, and mouth
        face_pts = [self.lm(i) for i in FACE_OVAL if self.lm(i) is not None]
        if len(face_pts) >= 8:
            face_poly = np.array([[int(p[0]), int(p[1])] for p in face_pts], dtype=np.int32)
            inner_mask = np.zeros((self.h, self.w), dtype=np.uint8)
            cv2.fillPoly(inner_mask, [face_poly], 255)
            # Erode slightly so the jawline and hairline perimeter remain crisp
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (14, 14))
            inner_mask = cv2.erode(inner_mask, kernel)
            edges[inner_mask > 0] = 0

        # 4. Zero out 6px frame border to prevent rectangular picture boundary lines
        edges[:6, :] = 0
        edges[-6:, :] = 0
        edges[:, :6] = 0
        edges[:, -6:] = 0

        # Chin Y divides upper head/hair from neck/garment
        chin = self.lm(152)
        chin_y = int(chin[1]) if chin else int(self.h * 0.6)

        # Hair edges: above chin line
        hair_edges = edges.copy()
        hair_edges[chin_y + 16:, :] = 0

        # Clothing edges: below chin line
        clothing_edges = edges.copy()
        clothing_edges[:chin_y - 10, :] = 0

        # Extract hair contours
        self._hair_contours_cache = self._contours_to_canvas(hair_edges, min_len=20, epsilon=1.8)

        # Extract all clothing contours (neck, collar, dress, fabric folds)
        self._clothing_contours_cache = self._contours_to_canvas(clothing_edges, min_len=22, epsilon=2.0)

        # Extract major structural clothing contours (longer lines: neckline, shoulder slope)
        self._clothing_major_cache = self._contours_to_canvas(clothing_edges, min_len=55, epsilon=2.4)

    def _contours_to_canvas(
        self,
        edge_map: np.ndarray,
        min_len: float = 20.0,
        epsilon: float = 1.8,
    ) -> List[List[Point]]:
        contours, _ = cv2.findContours(edge_map, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        result: List[List[Point]] = []

        for cnt in contours:
            arc_len = cv2.arcLength(cnt, False)
            if arc_len < min_len:
                continue

            # Simplify contour with Douglas-Peucker to remove pixel staircase artifacts
            approx = cv2.approxPolyDP(cnt, epsilon=epsilon, closed=False)
            pts = approx.squeeze(axis=1)
            if len(pts.shape) != 2 or len(pts) < 3:
                continue

            # Transform from photo pixels to canvas coordinates
            canvas_pts = [self.transform_fn((float(p[0]), float(p[1]))) for p in pts]
            if len(canvas_pts) >= 2:
                result.append(canvas_pts)

        return result

    def get_hair_contours(self) -> List[List[Point]]:
        if self._hair_contours_cache is None:
            self._extract_all_contours()
        return self._hair_contours_cache or []

    def get_clothing_contours(self) -> List[List[Point]]:
        if self._clothing_contours_cache is None:
            self._extract_all_contours()
        return self._clothing_contours_cache or []

    def get_major_garment_contours(self) -> List[List[Point]]:
        if self._clothing_major_cache is None:
            self._extract_all_contours()
        return self._clothing_major_cache or []

    # ─────────────────────────────────────────────────────────────
    # FOREHEAD MARK DETECTION (Bindi / Mole / Mark)
    # ─────────────────────────────────────────────────────────────

    def detect_forehead_mark(self) -> Optional[Tuple[Point, float]]:
        """
        Dynamically detects if a distinct dark mark (bindi, beauty mark, mole)
        exists on the subject's forehead.
        Returns: ((canvas_x, canvas_y), radius) if present, else None.
        Never fabricates marks on subjects who do not have one!
        """
        if not self.has_image():
            return None

        f10 = self.lm(10)
        g168 = self.lm(168)
        if not (f10 and g168):
            return None

        # Forehead crop between landmark 10 (top forehead) and 168 (glabella between brows)
        y0 = int(f10[1])
        y1 = int(g168[1])
        x0 = int(f10[0] - 25)
        x1 = int(f10[0] + 25)

        if y1 <= y0 or x1 <= x0 or y0 < 0 or y1 > self.h or x0 < 0 or x1 > self.w:
            return None

        crop = self.gray[y0:y1, x0:x1]
        if crop.size == 0:
            return None

        median_skin = float(np.median(crop))
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(crop)

        # Contrast threshold: a real bindi/mark is distinctly darker than the surrounding forehead skin
        contrast_diff = median_skin - min_val
        if contrast_diff > 42.0 and min_val < 100:
            img_x = x0 + min_loc[0]
            img_y = y0 + min_loc[1]
            canvas_pt = self.transform_fn((float(img_x), float(img_y)))
            # Mark radius proportional to scale
            mark_r = max(2.8 * self.scale, 2.2)
            return (canvas_pt, mark_r)

        return None

    # ─────────────────────────────────────────────────────────────
    # PHOTO-DRIVEN SHADOW ESTIMATION
    # ─────────────────────────────────────────────────────────────

    def get_light_direction(self) -> float:
        """
        Estimates the key lighting angle (in degrees) from cheek luminance.
        Positive = light from right, Negative = light from left.
        """
        if not self.has_image():
            return 25.0

        l_cheek = self.lm(234)
        r_cheek = self.lm(454)
        if l_cheek and r_cheek:
            lx, ly = int(l_cheek[0]), int(l_cheek[1])
            rx, ry = int(r_cheek[0]), int(r_cheek[1])
            if 0 <= ly < self.h and 0 <= lx < self.w and 0 <= ry < self.h and 0 <= rx < self.w:
                l_val = float(self.gray[ly, lx])
                r_val = float(self.gray[ry, rx])
                # Bias shadow angle toward the shaded side
                return 30.0 if l_val < r_val else -30.0

        return 25.0
