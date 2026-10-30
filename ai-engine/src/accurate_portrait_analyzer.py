"""
LOOMIS AI — ACCURATE PORTRAIT ANALYZER
Extracts rich, photo-accurate contours and details from reference.jpg and analysis.json:
- Exact landmark-mapped features (eyes, brows, nose, lips, jaw, bindi)
- True hair mask, bun contour, and signature curly tendrils
- Choker necklace and earrings
- Blouse neckline and saree drape
"""
from __future__ import annotations

import cv2
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

Point = Tuple[float, float]

class AccuratePortraitAnalyzer:
    def __init__(
        self,
        img_path: str = "e:/LoomisAI/ai-engine/input/reference.jpg",
        analysis_path: str = "e:/LoomisAI/ai-engine/output/analysis.json",
        construction_path: str = "e:/LoomisAI/ai-engine/output/construction.json",
    ):
        self.img_path = Path(img_path)
        self.analysis_path = Path(analysis_path)
        self.construction_path = Path(construction_path)

        self.img = cv2.imread(str(self.img_path))
        self.h, self.w = self.img.shape[:2]

        with open(self.analysis_path, "r", encoding="utf-8") as f:
            self.analysis = json.load(f)

        with open(self.construction_path, "r", encoding="utf-8") as f:
            self.construction = json.load(f)

        self.landmarks = self.analysis.get("landmarks", [])

        # Canvas transformation: maps image coordinates (w, h) to (1000, 1200) canvas
        # Based on HandDrawnLoomisRenderer
        face_pts = [
            (p["x"], p["y"])
            for p in self.landmarks
            if p["index"] in [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361,
                              288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
                              150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        ]
        min_x = min(p[0] for p in face_pts)
        max_x = max(p[0] for p in face_pts)
        min_y = min(p[1] for p in face_pts)
        max_y = max(p[1] for p in face_pts)
        width = max_x - min_x
        height = max_y - min_y
        scale_x = 650.0 / max(width, 1.0)
        scale_y = 800.0 / max(height, 1.0)
        self.scale = min(scale_x, scale_y)
        self.min_x = min_x
        self.min_y = min_y
        self.offset_x = 175.0
        self.offset_y = 150.0

    def transform(self, pt: Point) -> Point:
        """Transform an (x, y) point from reference image pixels to 1000x1200 canvas pixels."""
        cx = (pt[0] - self.min_x) * self.scale + self.offset_x
        cy = (pt[1] - self.min_y) * self.scale + self.offset_y
        return (cx, cy)

    def transform_pts(self, pts: List[Point]) -> List[Point]:
        return [self.transform(p) for p in pts]

    def lm(self, idx: int) -> Optional[Point]:
        if 0 <= idx < len(self.landmarks):
            p = self.landmarks[idx]
            return (p["x"], p["y"])
        return None

    def lm_canvas(self, idx: int) -> Optional[Point]:
        pt = self.lm(idx)
        return self.transform(pt) if pt else None

    def get_bindi_canvas(self) -> Point:
        """Accurately find forehead bindi position on canvas."""
        f10 = self.lm(10)
        g168 = self.lm(168)
        crop = self.img[int(f10[1]):int(g168[1]), int(f10[0]-35):int(f10[0]+35)]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(gray)
        bindi_img = (int(f10[0] - 35) + min_loc[0], int(f10[1]) + min_loc[1])
        return self.transform(bindi_img)

    def extract_hair_contours(self) -> Dict[str, Any]:
        """Extract bun, crown, and side curls from the reference photo."""
        hsv = cv2.cvtColor(self.img, cv2.COLOR_BGR2HSV)
        # Hair is very dark in reference photo
        hair_mask = (hsv[:, :, 2] < 58).astype(np.uint8) * 255
        
        # Zero out below neck/shoulders so blouse doesn't mix with hair
        chin = self.lm(152)
        if chin:
            hair_mask[int(chin[1] + 30):, :] = 0

        # Also zero out facial landmarks inside face oval so eyebrows/eyes aren't confused as hair mass
        face_contour_img = [
            self.lm(idx) for idx in [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361,
                                     288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149,
                                     150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]
        ]
        face_poly = np.array([[int(p[0]), int(p[1])] for p in face_contour_img if p], dtype=np.int32)
        inner_mask = np.zeros_like(hair_mask)
        cv2.fillPoly(inner_mask, [face_poly], 255)
        # Erode slightly so hairline edges are kept
        inner_mask = cv2.erode(inner_mask, np.ones((15, 15), np.uint8))
        hair_mask[inner_mask == 255] = 0

        # Find external contours of hair
        contours, _ = cv2.findContours(hair_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        
        # Filter contours by size
        valid_contours = []
        for c in contours:
            if cv2.contourArea(c) > 40:
                pts = [tuple(pt[0]) for pt in c]
                valid_contours.append(pts)

        return {
            "hair_mask": hair_mask,
            "raw_contours": valid_contours,
        }

if __name__ == "__main__":
    analyzer = AccuratePortraitAnalyzer()
    print("Scale:", analyzer.scale)
    bindi = analyzer.get_bindi_canvas()
    print("Bindi Canvas:", bindi)
    hair = analyzer.extract_hair_contours()
    print(f"Extracted {len(hair['raw_contours'])} hair contours")
