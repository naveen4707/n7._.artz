"""Build controlled prompts for Loomis AI generative enhancement."""

from __future__ import annotations

STAGE_NAMES = {
    1: "cranium construction",
    2: "center axis construction",
    3: "eye plane construction",
    4: "jaw construction",
    5: "nose construction",
    6: "mouth construction",
    7: "complete Loomis construction",
}


def build_enhancement_prompt(
    stage_number: int,
    preserve_geometry: bool = True,
) -> str:
    """Return a conservative prompt that enhances drawing appearance."""
    stage = STAGE_NAMES.get(stage_number, "Loomis construction")

    geometry_rule = (
        "Preserve the existing geometry, proportions, landmarks, placement, "
        "pose, construction lines, and stage content exactly."
        if preserve_geometry
        else
        "Keep the existing construction and proportions consistent."
    )

    return f"""
You are enhancing a Loomis-method instructional drawing.

Current stage: {stage}.

{geometry_rule}

Transform ONLY the visual rendering into a convincing traditional graphite
pencil construction drawing on lightly textured off-white drawing paper.

Desired appearance:
- real graphite pencil marks
- varied pencil pressure
- subtle overlapping exploratory strokes
- natural hand-drawn irregularity
- soft graphite buildup
- faint construction guides where they already exist
- darker structural lines where already emphasized
- believable paper grain
- clean instructional-art presentation
- monochrome graphite, no color

Do NOT:
- turn it into a photorealistic portrait
- replace the construction with a finished digital illustration
- change facial proportions
- change head pose
- invent facial features
- move the eyes, nose, mouth, jaw, axis, or planes
- remove the Loomis construction logic
- add text, labels, signatures, borders, watermarks, or UI

The result must still clearly look like a human artist's Loomis construction
drawing created progressively with pencil.
""".strip()
