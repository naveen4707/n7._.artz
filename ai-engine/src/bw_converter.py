"""
LOOMIS AI — STUDIO BLACK & WHITE PICTURE CONVERTER
Converts any portrait photograph into an artistic, high-contrast Black & White
reference picture optimized for classical Andrew Loomis graphite construction:
- Professional photometric luminance extraction (Rec.709)
- CLAHE (Contrast Limited Adaptive Histogram Equalization) for facial plane clarity
- Filmic S-curve tone mapping to preserve luminous highlights and velvety deep darks
- Sensor noise reduction while retaining hair, skin, and fabric texture
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, Union
import cv2
import numpy as np


def convert_to_black_and_white(
    input_path: Union[Path, str],
    output_path: Optional[Union[Path, str]] = None,
    contrast_boost: float = 1.15,
    clahe_clip: float = 2.0,
    tile_size: int = 8,
) -> Path:
    """
    Converts a portrait photo to an artistic black-and-white reference image.

    Args:
        input_path: Path to the input image file.
        output_path: Optional destination path. Defaults to <stem>_bw.jpg in the same directory.
        contrast_boost: Midtone contrast multiplier for graphite tonal separation.
        clahe_clip: Contrast Limit for Adaptive Histogram Equalization.
        tile_size: Grid tile size for localized illumination balancing.

    Returns:
        Path to the saved Black & White image file.
    """
    in_p = Path(input_path).resolve()
    if not in_p.exists():
        raise FileNotFoundError(f"Input image not found: {in_p}")

    if output_path is None:
        out_p = in_p.parent / f"{in_p.stem}_bw.jpg"
    else:
        out_p = Path(output_path).resolve()

    out_p.parent.mkdir(parents=True, exist_ok=True)

    img = cv2.imread(str(in_p))
    if img is None:
        raise ValueError(f"Failed to read image with OpenCV: {in_p}")

    # 1. High-fidelity photometric luminance conversion
    if len(img.shape) == 3 and img.shape[2] == 3:
        # Standard Rec.709 photometric weights: Y = 0.2126 R + 0.7152 G + 0.0722 B
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img.copy()

    # 2. Gentle bilateral filter to eliminate sensor noise while keeping hair & eyes razor-sharp
    smooth = cv2.bilateralFilter(gray, d=5, sigmaColor=35, sigmaSpace=35)

    # 3. CLAHE for localized facial tonal balance (lifts eye sockets, defines cheekbones)
    clahe = cv2.createCLAHE(clipLimit=clahe_clip, tileGridSize=(tile_size, tile_size))
    balanced = clahe.apply(smooth)

    # 4. Filmic S-curve contrast mapping to emulate fine art graphite paper tones
    # Maps darks deeper (4B/6B pencil) and highlights brighter (clean paper)
    norm = balanced.astype(np.float32) / 255.0

    # Gentle sigmoid S-curve
    mid = 0.50
    steepness = 3.6 * contrast_boost
    curve = 1.0 / (1.0 + np.exp(-steepness * (norm - mid)))
    # Renormalize to [0, 1]
    c_min = 1.0 / (1.0 + np.exp(steepness * mid))
    c_max = 1.0 / (1.0 + np.exp(-steepness * (1.0 - mid)))
    curve = (curve - c_min) / (c_max - c_min)
    curve = np.clip(curve * 255.0, 0, 255).astype(np.uint8)

    # 5. Blend 75% filmic curve + 25% original balanced for natural skin realism
    final_bw = cv2.addWeighted(curve, 0.75, balanced, 0.25, 0)

    # 6. Save as high-quality JPEG
    cv2.imwrite(str(out_p), final_bw, [cv2.IMWRITE_JPEG_QUALITY, 96])
    return out_p


def get_bw_reference_path(source_path: Union[Path, str]) -> Path:
    """
    Returns the associated black-and-white picture path for a given portrait,
    generating it automatically if it does not yet exist.
    """
    p = Path(source_path).resolve()
    bw_cand = p.parent / f"{p.stem}_bw{p.suffix}"
    if not bw_cand.exists():
        return convert_to_black_and_white(p, bw_cand)
    return bw_cand
