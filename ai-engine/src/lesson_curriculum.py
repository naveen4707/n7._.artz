"""
LOOMIS AI — INTERACTIVE DRAWING LESSON CURRICULUM & CHECKPOINTS
Pedagogical step-by-step guidance system for the student / artist.

Provides:
  - Definitive Andrew Loomis pedagogical principles and drawing rules for all 20 stages
  - Step-by-step actionable physical drawing instructions
  - Professional studio tips (pencil grip, arm movement, pressure control)
  - Common beginner pitfalls and actionable fixes
  - 3-point interactive checkpoint rubrics for stage self-assessment
  - Check-for-understanding self-test questions
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


LESSON_CURRICULUM: Dict[int, Dict[str, Any]] = {
    1: {
        "stage": 1,
        "title": "Cranial Sphere & 3D Head Tilt",
        "category": "Loomis Foundation",
        "pencil_grade": "4H Extra Hard Graphite",
        "stroke_type": "Whispering circular ghost lines",
        "estimated_duration_min": 5,
        "learning_objective": "Establish the 3D volume of the skull and lock its spatial tilt in space before attempting any facial features.",
        "loomis_core_rule": "The ball of the head is the primary cranial anchor. The skull is basically a ball, flattened at the sides. Everything hangs from this primary 3D sphere.",
        "step_by_step_instructions": [
            "Hold your 4H pencil loosely at a 30-degree angle from the paper, engaging your shoulder rather than your wrist.",
            "Draw a fluid, whispering sphere in the upper two-thirds of your paper. Don't worry about drawing a single stiff circle—overlap 3 to 4 faint concentric passes.",
            "Establish the tilt axis through the center of the sphere, reflecting whether the head is tilted forward, back, or sideways.",
            "Lightly mark the top and bottom poles of the sphere to anchor its 3D orientation in perspective.",
        ],
        "pro_tips": [
            "Keep your pencil marks so faint that they could easily be lifted with a kneaded eraser without leaving a groove.",
            "Step back 4 feet from your easel or desk: the cranial ball should look balanced on the page before you proceed.",
        ],
        "common_pitfalls": [
            "Drawing a flattened oval or egg instead of a solid 3D sphere.",
            "Pressing too hard with a soft pencil (2B/4B), which leaves indelible grooves in the paper.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Cranial ball is drawn as a true circular sphere, not an elongated egg."},
            {"id": "c2", "text": "Tilt axis line clearly establishes the 3D angle of the head in space."},
            {"id": "c3", "text": "Pencil strokes are whisper-light (4H) and easily erasable."},
        ],
        "mastery_question": {
            "question": "Why does Andrew Loomis begin with a 3D sphere rather than the oval of the face?",
            "options": [
                "Because the sphere represents the solid bone volume of the braincase that cannot change shape.",
                "Because spheres are easier to shade than facial features.",
                "Because human heads are perfectly spherical without flat planes.",
            ],
            "correct_index": 0,
            "explanation": "The cranial sphere represents the immutable cranium/braincase. The jaw is a movable appendage that attaches to this primary solid volume.",
        },
    },
    2: {
        "stage": 2,
        "title": "Brow Equator & Central Facial Axis",
        "category": "Loomis Foundation",
        "pencil_grade": "4H Hard Graphite",
        "stroke_type": "Curved great-circle spherical arcs",
        "estimated_duration_min": 6,
        "learning_objective": "Map the 3D equator and central meridian across the curved sphere surface to establish perspective pitch and yaw.",
        "loomis_core_rule": "The brow line wraps around the sphere like an equator. The facial centerline bisects the sphere from the crown to the chin. Together, they dictate the perspective of every feature.",
        "step_by_step_instructions": [
            "Draw the horizontal brow equator curving around the surface of the cranial ball like a ring on a globe.",
            "If the subject is looking down, the brow line curves downward; if looking up, it bows upward.",
            "Drop the central facial meridian vertically across the center of the face, intersecting the brow line at the glabella keystone.",
            "Extend the vertical axis downward below the sphere by approximately half the sphere's radius to reserve space for the jaw.",
        ],
        "pro_tips": [
            "Think of the brow line as a rubber band stretched around a basketball.",
            "The intersection point of the brow line and central axis is the landmark for the bridge of the nose and glabella.",
        ],
        "common_pitfalls": [
            "Drawing the brow line as a straight ruler line, which instantly destroys the illusion of 3D depth.",
            "Placing the central axis in the geometric middle when the subject is turned in 3/4 perspective.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Brow line wraps around the curved surface with realistic perspective bowing."},
            {"id": "c2", "text": "Vertical center axis curves across the front meridian of the sphere."},
            {"id": "c3", "text": "Intersection accurately reflects the subject's pitch (up/down) and yaw (turned)."},
        ],
        "mastery_question": {
            "question": "What happens to the brow equator when the head is tilted upward?",
            "options": [
                "It curves upward like a smile, exposing the underplane of the chin and nose.",
                "It becomes a straight horizontal line.",
                "It curves downward toward the floor.",
            ],
            "correct_index": 0,
            "explanation": "Looking up at a sphere causes all horizontal cross-sections (equator and thirds) to curve upward like ellipses viewed from below.",
        },
    },
    3: {
        "stage": 3,
        "title": "Side Cranial Discs & Eye Plane",
        "category": "Loomis Foundation",
        "pencil_grade": "2H Hard Graphite",
        "stroke_type": "Elliptical slice curves and 4-quadrant cross",
        "estimated_duration_min": 7,
        "learning_objective": "Carve the flat side planes of the skull and locate the ear hinge position.",
        "loomis_core_rule": "The skull is not a perfect sphere; it is flattened on both sides. Slicing off these vertical side discs establishes the temporal planes and gives the skull its true anatomical width.",
        "step_by_step_instructions": [
            "On the visible side of the sphere, slice off a circular disc about two-thirds the height of the cranial ball.",
            "Draw a vertical cross line through the disc center (pointing to the jaw hinge) and a horizontal cross line (aligned with the brow equator).",
            "The center of this side disc is the exact anatomical location where the ear canal and ear attach.",
            "Drop the parallel eye plane guideline slightly below the brow line.",
        ],
        "pro_tips": [
            "In a 3/4 view, the near side disc appears as a wide ellipse, while the far side is nearly hidden by perspective foreshortening.",
            "The horizontal cross of the side disc always points directly into the brow equator.",
        ],
        "common_pitfalls": [
            "Making the side disc too small or placing it too far forward on the face.",
            "Forgetting that the ear attaches in the lower-back quadrant of the side disc.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Side temporal disc is sliced off with height approximately 2/3 of sphere."},
            {"id": "c2", "text": "Disc crosshairs clearly establish the ear attachment and jaw hinge point."},
            {"id": "c3", "text": "Eye plane guideline runs parallel to the brow equator."},
        ],
        "mastery_question": {
            "question": "Where does the top of the ear attach relative to the side cranial disc?",
            "options": [
                "At the level of the horizontal crosshair that aligns with the brow equator.",
                "At the very top of the cranial sphere.",
                "At the bottom of the chin wedge.",
            ],
            "correct_index": 0,
            "explanation": "Andrew Loomis notes that the top of the ear aligns precisely with the horizontal line passing through the center of the side disc, connecting to the brow line.",
        },
    },
    4: {
        "stage": 4,
        "title": "Jaw Construction & Mandible Rhythm",
        "category": "Loomis Foundation",
        "pencil_grade": "2H Hard Graphite",
        "stroke_type": "Sweeping bucket-handle architectural curves",
        "estimated_duration_min": 8,
        "learning_objective": "Swing the mandible down from the ear hinges to establish the front jaw plane and chin wedge.",
        "loomis_core_rule": "The jaw is like a bucket handle swinging down from the ear hinges. It drops vertically to the gonial angle, then angles forward to the flat front plane of the chin.",
        "step_by_step_instructions": [
            "From the ear hinge at the center of the side disc, drop a line down and slightly back to the gonial angle of the jaw.",
            "Angle the jawline forward from the gonion toward the chin along the mandibular rhythm line.",
            "Draw the front plane of the chin as a trapezoidal wedge centered squarely on the central facial axis.",
            "Connect the jaw rhythm from both sides to form a solid, unified bucket handle.",
        ],
        "pro_tips": [
            "Female jaws typically feature a softer, more rounded gonial angle, whereas male jaws are more angular and square.",
            "Check that the chin center aligns strictly with the vertical facial meridian.",
        ],
        "common_pitfalls": [
            "Drawing the jaw directly attached to the neck without establishing the mandibular corner (gonion).",
            "Skewing the chin to one side so it slips off the facial centerline.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Jaw lines originate securely from the ear hinge at the side disc."},
            {"id": "c2", "text": "Gonial corner of the jaw is established before angling forward to chin."},
            {"id": "c3", "text": "Chin front plane is centered on the central facial axis."},
        ],
        "mastery_question": {
            "question": "What is the primary anatomical metaphor Andrew Loomis uses for the jaw?",
            "options": [
                "A bucket handle swinging from hinges on either side of the skull.",
                "A rectangular box glued to the bottom of the sphere.",
                "A triangular cone pointing to the floor.",
            ],
            "correct_index": 0,
            "explanation": "Loomis famously described the jaw as swinging like a bucket handle from the pivot points just below the ears.",
        },
    },
    5: {
        "stage": 5,
        "title": "Nose Keystones & Midface Proportion",
        "category": "Loomis Foundation",
        "pencil_grade": "H Graphite",
        "stroke_type": "Rule of Thirds guide arches and keystone wedge",
        "estimated_duration_min": 7,
        "learning_objective": "Apply the classical Loomis Rule of Thirds to position the hairline, brow, nose base, and chin.",
        "loomis_core_rule": "The face divides into three equal units: from the hairline to the brow, from the brow to the bottom of the nose, and from the nose base to the bottom of the chin.",
        "step_by_step_instructions": [
            "Measure the distance from the brow line to the top of the cranial sphere to mark the hairline (top third).",
            "Transfer that exact distance downward from the brow line along the central axis to mark the nose base (middle third).",
            "Verify that the remaining distance from nose base to chin bottom equals the other two units (lower third).",
            "Construct the trapezoidal keystone wedge between the eyebrows where the nasal bone anchors to the forehead.",
        ],
        "pro_tips": [
            "In upward head tilts, the upper third is foreshortened and compressed, while the lower third expands.",
            "Use your pencil as a sighting tool: measure with your thumb against the pencil shaft to compare the thirds.",
        ],
        "common_pitfalls": [
            "Blindly making thirds equal without accounting for perspective tilt foreshortening.",
            "Placing the nose base too low, which crowds the lips and elongates the midface.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Hairline, brow, nose base, and chin levels adhere to the Rule of Thirds."},
            {"id": "c2", "text": "Perspective foreshortening is respected for tilted head poses."},
            {"id": "c3", "text": "Glabella keystone is positioned firmly between the eyes at the bridge root."},
        ],
        "mastery_question": {
            "question": "What are the three canonical divisions of the Loomis facial proportion rule?",
            "options": [
                "Hairline to Brow, Brow to Nose Base, Nose Base to Chin Bottom.",
                "Forehead to Eyes, Eyes to Mouth, Mouth to Neck.",
                "Crown to Ears, Ears to Nose, Nose to Collarbone.",
            ],
            "correct_index": 0,
            "explanation": "The Andrew Loomis Rule of Thirds divides the facial mask into three equal proportions: Hairline-Brow, Brow-Nose Base, and Nose Base-Chin.",
        },
    },
    6: {
        "stage": 6,
        "title": "Mouth Rhythm & Dental Muzzle",
        "category": "Loomis Foundation",
        "pencil_grade": "H Graphite",
        "stroke_type": "Cylindrical dental arc and oral fissure rhythm",
        "estimated_duration_min": 7,
        "learning_objective": "Construct the cylindrical dental muzzle that anchors the lips and curves into the jaw.",
        "loomis_core_rule": "The teeth and jaw form a barrel or cylinder (the dental muzzle). The lips curve around this cylinder like a ribbon wrapped on a tin can.",
        "step_by_step_instructions": [
            "Divide the lower third (nose base to chin) into three sub-thirds.",
            "Place the line of closure of the lips at the upper third mark below the nose base.",
            "Draw the dental barrel: a rounded cylindrical arc curving outward from the canine teeth back toward the corners of the mouth.",
            "Mark the corner nodes (modiolus) of the mouth, which align vertically with the inner irises.",
        ],
        "pro_tips": [
            "Never draw the lips flat! Always wrap them around the cylinder of the dental arc.",
            "The corner nodes of the mouth tuck inward and catch a dark shadow accent in every lighting condition.",
        ],
        "common_pitfalls": [
            "Drawing lips as two flat pointed leaves pasted onto a flat face.",
            "Placing the mouth halfway between nose and chin instead of one-third down.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Oral fissure is placed one-third of the way down from nose base to chin."},
            {"id": "c2", "text": "Dental muzzle curves around the facial cylinder in 3D perspective."},
            {"id": "c3", "text": "Corner nodes are mapped with proper width aligned with inner eye pupils."},
        ],
        "mastery_question": {
            "question": "Why do the corners of the lips appear to curve backward in 3/4 perspective?",
            "options": [
                "Because they wrap around the cylindrical dental arc of the teeth.",
                "Because the mouth is always smiling in Loomis drawings.",
                "Because lips shrink toward the back of the head.",
            ],
            "correct_index": 0,
            "explanation": "The lips wrap around the cylindrical barrel of the teeth (dental arch), meaning the far corner wraps back around the curve in 3D perspective.",
        },
    },
    7: {
        "stage": 7,
        "title": "Unified Loomis Structural Armature",
        "category": "Loomis Foundation",
        "pencil_grade": "HB Medium Graphite",
        "stroke_type": "Confirmed structural construction lines",
        "estimated_duration_min": 8,
        "learning_objective": "Step back and verify all proportional relationships, perspective alignments, and 3D volumes before rendering facial details.",
        "loomis_core_rule": "Do not rush into drawing the eyes or lips until the head structure is indisputably sound. If your foundation is solid, features fall naturally into place.",
        "step_by_step_instructions": [
            "Step back 5 feet and inspect the unified armature as a complete 3D wireframe in space.",
            "Verify the 5 Eyes Rule: the face is five eye-widths across at the eye level.",
            "Confirm that the brow equator, eye line, nose base, and mouth line all share a common vanishing perspective.",
            "Gently reinforce the confirmed structural lines with an HB pencil while leaving the initial 4H scaffolding visible.",
        ],
        "pro_tips": [
            "Hold your drawing up to a mirror or view it in reverse: any balance errors will pop out immediately.",
            "A solid 10 minutes spent perfecting Stage 7 saves 2 hours of painful erasing during feature rendering.",
        ],
        "common_pitfalls": [
            "Rushing into shading before confirming facial symmetry and head perspective.",
            "Erasing all scaffolding: Loomis drawings draw strength from visible underdrawing scaffolding.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Complete 3D wireframe armature is balanced and proportioned."},
            {"id": "c2", "text": "All horizontal facial planes share coherent perspective alignment."},
            {"id": "c3", "text": "Interocular spacing conforms to the Five Eyes proportional rule."},
        ],
        "mastery_question": {
            "question": "What is the Five Eyes Rule in classical portrait proportion?",
            "options": [
                "The total width of the head at eye level equals five eye-widths.",
                "Portraits must always include five guide eyes.",
                "The distance from forehead to chin is five eye-widths.",
            ],
            "correct_index": 0,
            "explanation": "At eye level, the width of the head is equal to five eye-widths: one eye width on each temple, one between the eyes, and the two eyes themselves.",
        },
    },
    8: {
        "stage": 8,
        "title": "Eye Spheres & Orbital Socket Boundaries",
        "category": "Anatomical Features",
        "pencil_grade": "HB Medium Graphite",
        "stroke_type": "Spherical eyeball encasements and socket facets",
        "estimated_duration_min": 8,
        "learning_objective": "Construct the spherical eyeballs nestled deep inside the bony orbital cavern.",
        "loomis_core_rule": "The eyeball is a sphere resting within a bony socket. The eyelids are thin sheets of tissue wrapped over the curve of this sphere.",
        "step_by_step_instructions": [
            "Block in the bony orbital socket: a rectangular-to-octagonal cavern beneath the brow ridge.",
            "Sketch the eyeball as a true 3D sphere resting inside the socket.",
            "Ensure the distance between the two eye spheres equals exactly one eye diameter.",
            "Notice how the eyeball projects slightly forward, creating the corneal dome oriented with head yaw.",
        ],
        "pro_tips": [
            "The eyeball does not sit flush with the forehead; it recedes approximately 15mm back under the protective brow bone.",
            "Use light circular motions to feel the spherical form before defining the eyelid slits.",
        ],
        "common_pitfalls": [
            "Drawing the eye as a 2D flat almond shape without understanding the sphere beneath.",
            "Placing the eyes too close together or too far apart.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Both eye spheres are constructed within the orbital socket boundary."},
            {"id": "c2", "text": "Interocular space between eye spheres equals one eye width."},
            {"id": "c3", "text": "Eye depth recedes realistically beneath the superciliary brow shelf."},
        ],
        "mastery_question": {
            "question": "Why do eyelids curve asymmetrically across the eye?",
            "options": [
                "Because they wrap over the spherical curvature of the eyeball.",
                "Because eyelashes pull the skin sideways.",
                "Because the lower lid is twice as heavy as the upper lid.",
            ],
            "correct_index": 0,
            "explanation": "The eyelids are curved membranes wrapped over a spherical globe, creating an asymmetric great-circle arc in perspective.",
        },
    },
    9: {
        "stage": 9,
        "title": "Eyelid Thickness, Iris & Pupil Placement",
        "category": "Anatomical Features",
        "pencil_grade": "2B Soft Graphite",
        "stroke_type": "Kohl-rimmed contours, dark pupil core, and specular lift",
        "estimated_duration_min": 9,
        "learning_objective": "Render anatomical eyelid thickness planes, limbal rings, 6B pupil cores, and pure-white catchlights.",
        "loomis_core_rule": "Eyelids have thickness! The upper lid plane faces downward; the lower lid plane faces upward to catch the light. The pupil anchors the living gaze.",
        "step_by_step_instructions": [
            "Draw the upper eyelid wrapping over the sphere with a firm, dark kohl stroke. Peak the curve slightly toward the inner third.",
            "Draw the lower eyelid with a lighter stroke, peaking its lowest point slightly toward the outer third.",
            "Show the visible shelf/thickness of the eyelid margin (especially on the lower lid).",
            "Fill the pupil with deep 6B graphite, leaving a crisp, pure-white specular catchlight.",
        ],
        "pro_tips": [
            "The upper eyelid always casts a thin cast shadow onto the top of the iris and sclera.",
            "Never color the sclera pure white; it is a sphere in space with subtle gray shading at both corners.",
        ],
        "common_pitfalls": [
            "Drawing eyelids as razor-thin single lines with zero tissue thickness.",
            "Centering both the upper and lower eyelid curves symmetrically like a football.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Eyelid curves display realistic anatomical asymmetry (upper peaks in, lower dips out)."},
            {"id": "c2", "text": "Eyelid margin thickness is clearly indicated."},
            {"id": "c3", "text": "Pupil core is solid 6B dark with a luminous white specular catchlight."},
        ],
        "mastery_question": {
            "question": "Where does the peak of the upper eyelid curve typically sit?",
            "options": [
                "Slightly toward the inner corner (medial third).",
                "Dead center in the middle.",
                "At the extreme outer corner.",
            ],
            "correct_index": 0,
            "explanation": "Anatomically, the upper eyelid peaks about 1/3 of the way from the inner corner, while the lower lid dips lowest about 1/3 from the outer corner.",
        },
    },
    10: {
        "stage": 10,
        "title": "3-Part Eyebrow Architecture & Keystone",
        "category": "Anatomical Features",
        "pencil_grade": "B / 2B Graphite",
        "stroke_type": "Directional longitudinal hair flow and plane breaks",
        "estimated_duration_min": 7,
        "learning_objective": "Sculpt the three-part Loomis eyebrow mass (Head, Body, Tail) adhering to the superciliary ridge.",
        "loomis_core_rule": "The eyebrow is not a line—it is a planar mass adhering to the superciliary ridge. It divides into Head (vertical), Body (horizontal/upward), and Tail (downward-sloping).",
        "step_by_step_instructions": [
            "Identify the bone ridge of the supraorbital margin where the brow rests.",
            "Construct the Head of the brow rising vertically from the glabella keystone with light upward strokes.",
            "Sweep the Body horizontally across the brow shelf toward the temple with layered directional strokes.",
            "Angle the Tail downward toward the outer corner of the eye, tapering gracefully.",
        ],
        "pro_tips": [
            "Draw the eyebrow as a solid mass first before adding individual hair flicks along the edges.",
            "The brow tail should not drop lower than the brow head—keep it lifted to preserve youthful vitality.",
        ],
        "common_pitfalls": [
            "Drawing 'caterpillar' or 'comb-tooth' eyebrows with uniform parallel vertical lines.",
            "Placing the eyebrows too high above the actual bony eye socket rim.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Eyebrows follow the 3-part anatomical division (Head, Body, Tail)."},
            {"id": "c2", "text": "Hair direction transitions naturally from vertical (head) to angled (tail)."},
            {"id": "c3", "text": "Brow anchors solidly to the glabella keystone at the bridge root."},
        ],
        "mastery_question": {
            "question": "What are the three structural segments of an Andrew Loomis eyebrow?",
            "options": [
                "Head (rising from keystone), Body (spanning the shelf), and Tail (tapering down).",
                "Start, Middle, and Finish.",
                "Root, Arch, and Brow bone.",
            ],
            "correct_index": 0,
            "explanation": "Loomis divides the eyebrow into the Head (near the nose), the Body (across the brow ridge), and the Tail (tapering toward the temple).",
        },
    },
    11: {
        "stage": 11,
        "title": "5-Plane Sculpted Nose Construction",
        "category": "Anatomical Features",
        "pencil_grade": "HB / 2B Graphite",
        "stroke_type": "Planar wedge facets, tip ball, and crescent nostril cuts",
        "estimated_duration_min": 9,
        "learning_objective": "Construct the 5 classical planes of the nose: keystone root, dorsal bridge, 2 lateral side slopes, tip ball, and columella underplane.",
        "loomis_core_rule": "Think of the nose as a wedge or tent. It has a bridge roof, two sloping sides, and an underplane with the nostrils and septum. The tip is a rounded ball resting on the wedge.",
        "step_by_step_instructions": [
            "From the glabella keystone, drop the central dorsal ridge down to the nose tip ball.",
            "Construct the two lateral sloping planes angling from the dorsal ridge down to the alar grooves.",
            "Block in the nose tip as a firm spherical ball with subtle flat highlights.",
            "Angle the alar wings outward like curved parentheses hugging the tip.",
            "Carve the triangular columella underplane and indicate dark crescent nostril hollows beneath.",
        ],
        "pro_tips": [
            "Never draw hard dark lines down both sides of the nose bridge! Outline only the shadow side, letting light dissolve the other side.",
            "Nostrils are not black holes—they are curved slits hidden beneath the overhanging alar wings.",
        ],
        "common_pitfalls": [
            "Drawing nostrils as two black round dots facing directly forward.",
            "Drawing a single thin line for the nose bridge with no side planes.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "5-plane wedge structure (keystone, bridge, 2 side slopes, tip, underplane) is clear."},
            {"id": "c2", "text": "Nose tip ball and alar wings form harmonious spherical relationships."},
            {"id": "c3", "text": "Nostrils are shaded as subtle recessed slits under the columella."},
        ],
        "mastery_question": {
            "question": "Why should you avoid drawing a dark outline down both sides of the nose bridge?",
            "options": [
                "Because light strikes one side and casts a shadow on the other; outlining both flattens the form.",
                "Because noses only have one side.",
                "Because graphite rubs off on the bridge.",
            ],
            "correct_index": 0,
            "explanation": "Outlining both sides creates a flat cartoon strip. In reality, light illuminates one side and the bridge, while the opposite side slope falls into shadow.",
        },
    },
    12: {
        "stage": 12,
        "title": "5-Cushion Lip Architecture & Cupid's Bow",
        "category": "Anatomical Features",
        "pencil_grade": "2B Soft Graphite",
        "stroke_type": "Curved cushion contours and sinuous closure line",
        "estimated_duration_min": 8,
        "learning_objective": "Model the 5 anatomical cushions of the lips: 3 upper lip tubercles and 2 lower lip cushions.",
        "loomis_core_rule": "The upper lip has three cushions (a central tubercle and two wings); the lower lip has two oval pillows with a groove between them. The upper lip faces down and is always in shadow.",
        "step_by_step_instructions": [
            "Establish the sinuous line of closure: a subtle Cupid's bow dip in the center that rises gently and curves to the corner nodes.",
            "Construct the 3 upper lip cushions: the central teardrop tubercle and two flanking lateral wings.",
            "Construct the 2 lower lip cushions: two parallel horizontal pillows resting beneath the upper lip.",
            "Add the philtrum column connecting the Cupid's bow to the base of the nose.",
            "Carve the dark modiolus nodes at the mouth corners.",
        ],
        "pro_tips": [
            "The upper lip is almost universally darker in tone than the lower lip because it slopes downward away from overhead light.",
            "Leave a luminous highlight on the top crest of the lower lip cushion to give it full, succulent 3D volume.",
        ],
        "common_pitfalls": [
            "Drawing a harsh dark outline around the lower lip (it should fade softly into the chin).",
            "Ignoring the central depression between the two lower lip cushions.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "5-cushion architecture (3 upper, 2 lower) is distinctly modeled."},
            {"id": "c2", "text": "Line of closure has natural sinuous Cupid's bow rhythm."},
            {"id": "c3", "text": "Upper lip is shaded darker in value than the light-catching lower lip."},
        ],
        "mastery_question": {
            "question": "How many anatomical cushions comprise the human lips in Andrew Loomis's construction?",
            "options": [
                "Five: three in the upper lip and two in the lower lip.",
                "Two: one upper and one lower.",
                "Four: two upper and two lower.",
            ],
            "correct_index": 0,
            "explanation": "Loomis models the upper lip with three cushions (central tubercle and two lateral wings) and the lower lip with two oval cushions.",
        },
    },
    13: {
        "stage": 13,
        "title": "Zygomatic Arches & Planar Contours",
        "category": "Facial Contours",
        "pencil_grade": "HB Graphite",
        "stroke_type": "Subtle planar transition curves and malar rhythms",
        "estimated_duration_min": 7,
        "learning_objective": "Define the zygomatic cheekbone apex, temporal crest lines, and mental protuberance planes.",
        "loomis_core_rule": "The zygomatic arch is the high bridge connecting the cheek to the ear. It marks the widest point of the face and catches the primary high-key cheek highlight.",
        "step_by_step_instructions": [
            "Trace the zygomatic arch starting from the malar apex below the eye corner, angling toward the tragus of the ear.",
            "Establish the temporal crest lines running from the brow tail upward across the side of the forehead.",
            "Sculpt the mental protuberance (chin ball) as a firm round mass supported by the trapezoidal chin wedge.",
            "Lightly indicate the nasolabial fold arcs framing the mouth from the nostrils toward the jaw.",
        ],
        "pro_tips": [
            "The malar apex is the key landmark for catching light on the cheek; keep its highlight crisp.",
            "Keep facial contour lines soft—the cheek is an undulating organic landscape, not a sharp polygon.",
        ],
        "common_pitfalls": [
            "Making the cheeks look hollow or sunken by over-darkening the buccal depressions.",
            "Drawing the jawline as a ruler-straight line from ear to chin.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Zygomatic arch connects brow tail, malar apex, and ear tragus rhythmically."},
            {"id": "c2", "text": "Temporal crest line separates forehead front plane from side temple plane."},
            {"id": "c3", "text": "Chin ball is centered and defined as a volumetric 3D mass."},
        ],
        "mastery_question": {
            "question": "What is the primary visual role of the zygomatic arch in portrait lighting?",
            "options": [
                "It forms the high bone ridge of the cheek that catches the main key light and separates front from side.",
                "It holds the teeth in place.",
                "It forms the bridge of the nose.",
            ],
            "correct_index": 0,
            "explanation": "The zygomatic bone forms the cheekbone prominence that separates the front plane of the face from the receding side plane.",
        },
    },
    14: {
        "stage": 14,
        "title": "Ear Architecture & Perspective Foreshortening",
        "category": "Facial Contours",
        "pencil_grade": "HB Graphite",
        "stroke_type": "Curved helix rim, antihelix Y-fork, and concha bowl",
        "estimated_duration_min": 7,
        "learning_objective": "Construct the ear with accurate proportional bounds and 3D perspective foreshortening.",
        "loomis_core_rule": "The ear is aligned between two horizontal lines: the brow line at the top and the base of the nose at the bottom. In perspective, it slants backward parallel to the bridge of the nose.",
        "step_by_step_instructions": [
            "Confirm that the top of the ear aligns with the brow equator and the bottom aligns with the nose base.",
            "Draw the outer C-shaped helix rim curling inward at the top.",
            "Construct the inner antihelix with its distinct superior crus Y-fork.",
            "Carve the deep concha bowl hollow and indicate the small protective tragus flap.",
            "Add the soft lobule at the bottom, including earrings or ear ornaments if present.",
        ],
        "pro_tips": [
            "In 3/4 view, the near ear is viewed obliquely and appears narrower, while the far ear may be partially or completely occluded.",
            "The ear is not vertical—it angles backward roughly 15 degrees, matching the slope of the nasal bridge.",
        ],
        "common_pitfalls": [
            "Placing the ear too high on the cranial sphere or making it far too large.",
            "Drawing the ear as a flat question mark without the concha bowl cavity.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Ear bounds are strictly aligned between brow line (top) and nose base (bottom)."},
            {"id": "c2", "text": "Anatomical landmarks (helix, antihelix Y-fork, concha, tragus, lobule) are clear."},
            {"id": "c3", "text": "Perspective slant matches the slope of the head and nasal bridge."},
        ],
        "mastery_question": {
            "question": "Which two facial levels bound the height of the human ear in normal perspective?",
            "options": [
                "The brow equator level (top) and the nose base level (bottom).",
                "The hairline (top) and the mouth line (bottom).",
                "The eye line (top) and the chin bottom (bottom).",
            ],
            "correct_index": 0,
            "explanation": "Andrew Loomis emphasizes that the ear sits comfortably between the brow line (equator) at the top and the bottom of the nose at the base.",
        },
    },
    15: {
        "stage": 15,
        "title": "Volumetric Hair Envelope & Ribbon Flow",
        "category": "Hair & Silhouette",
        "pencil_grade": "2B / 4B Soft Graphite",
        "stroke_type": "Broad volumetric envelope arcs and ribbon S-curves",
        "estimated_duration_min": 9,
        "learning_objective": "Enclose the cranium in a volumetric hair envelope standing proud above the skull with directional ribbon flow.",
        "loomis_core_rule": "Draw the hair as large rhythmic masses and volumes, not as millions of separate hairs. Hair has thickness and stands 15–20mm above the bone of the skull.",
        "step_by_step_instructions": [
            "Draw the volumetric cranial hair envelope resting 15 to 22 pixels above the cranial sphere.",
            "Establish the hairline rhythm across the forehead third, observing widow's peaks, temple recesses, and sideburns.",
            "Lay down sweeping directional ribbon flow guidelines that follow the hairstyle (crown to bun, curls over shoulders).",
            "Group tumbling locks into distinct 3D ribbon chunks that overlap in space.",
        ],
        "pro_tips": [
            "Always draw the skull sphere first! Never draw hair floating in space without knowing where the skull is underneath.",
            "Use the side of your 4B graphite lead to lay in broad, soft hair mass tones quickly.",
        ],
        "common_pitfalls": [
            "Drawing hair directly on the skull line, making the subject look bald with hair painted on.",
            "Scratching thousands of tiny individual lines that produce messy, wiry hair.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Volumetric hair envelope stands proud above the underlying cranial sphere."},
            {"id": "c2", "text": "Hairline rhythm is accurately placed at the upper third level."},
            {"id": "c3", "text": "Hair is grouped into rhythmic, volumetric ribbon masses with directional flow."},
        ],
        "mastery_question": {
            "question": "Why must the hair contour sit above the cranial sphere line?",
            "options": [
                "Because real hair has thickness and volume that lifts it off the bone of the skull.",
                "Because human skulls grow smaller as people age.",
                "Because artists need extra room for signatures.",
            ],
            "correct_index": 0,
            "explanation": "Hair has physical volume and root lift; it naturally sits 1/2 to 1 inch above the cranial bone surface.",
        },
    },
    16: {
        "stage": 16,
        "title": "Cervical Column & Sternocleidomastoid (SCM)",
        "category": "Anatomy & Drapery",
        "pencil_grade": "2B Soft Graphite",
        "stroke_type": "Cylindrical column, muscular V-rhythm, and collarbone bars",
        "estimated_duration_min": 8,
        "learning_objective": "Anchor the head on a cylindrical neck with SCM muscles, clavicles, and trapezius slopes.",
        "loomis_core_rule": "The head does not balance on a stick; the neck is a sturdy cylinder angled slightly forward. The sternocleidomastoid muscles form a V from behind the ears down to the pit of the neck.",
        "step_by_step_instructions": [
            "Construct the neck cylinder emerging from behind the gonial jaw angles.",
            "Draw the sternocleidomastoid (SCM) muscle V-rhythm from the mastoid processes behind the ears down to the jugular pit.",
            "Indicate the suprasternal jugular notch (pit of the neck) at the base of the throat.",
            "Draw the horizontal handlebar curves of the clavicles (collarbones).",
            "Slope the trapezius muscles downward from the mid-neck to the acromion shoulder tips.",
        ],
        "pro_tips": [
            "When the head turns, the SCM muscle opposite the turning direction becomes taut and stands out prominently.",
            "Drape jewelry and necklaces around the true cylinder of the neck, curving downward like ellipses.",
        ],
        "common_pitfalls": [
            "Drawing the neck as two straight parallel vertical lines under the jaw.",
            "Making the neck too thin to plausibly support the heavy mass of the head.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Neck is constructed as a solid cylinder inclined slightly forward."},
            {"id": "c2", "text": "SCM muscles form a coherent V-rhythm from ears to jugular pit."},
            {"id": "c3", "text": "Clavicles and trapezius slopes establish stable shoulder foundation."},
        ],
        "mastery_question": {
            "question": "What is the function of the sternocleidomastoid (SCM) muscle in drawing?",
            "options": [
                "It forms the dynamic V-rhythm that visually connects the skull to the collarbones.",
                "It separates the eyes from the nose.",
                "It controls the movement of the lower lip.",
            ],
            "correct_index": 0,
            "explanation": "The SCM muscle pair connects behind each ear to the jugular pit, anchoring the head to the torso and defining the anatomical neck cylinder.",
        },
    },
    17: {
        "stage": 17,
        "title": "Facial Likeness & Cultural Ornamentation",
        "category": "Refinement & Likeness",
        "pencil_grade": "3B Soft Graphite",
        "stroke_type": "Delicate harmonic contours and punctate ornament accents",
        "estimated_duration_min": 8,
        "learning_objective": "Harmonize all individual facial features with the subject's distinct anatomical likeness and traditional ornamentation.",
        "loomis_core_rule": "Likeness depends on the precise proportional relationship between the features and the bone landmarks. Refine the organic contours while honoring authentic individual traits.",
        "step_by_step_instructions": [
            "Refine the continuous jawline and soft rounded chin curvature, eliminating any remaining boxiness.",
            "Verify the exact placement of identifying facial marks (such as a traditional bindi between the brow heads).",
            "Harmonize the eye corners with the nose bridge and the nostrils with the lip modiolus.",
            "Check that all anatomical features sit in perfect harmony with the subject's unique likeness.",
        ],
        "pro_tips": [
            "Squint your eyes to check the global value relationship: the likeness should read clearly even when blurry.",
            "Do not over-render tiny details—let the grand relationships carry the resemblance.",
        ],
        "common_pitfalls": [
            "Forcing generic facial features onto a unique portrait subject.",
            "Drawing cultural ornaments (like a bindi) floating disconnected from the forehead surface plane.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Jawline and chin contours transition organically into the neck."},
            {"id": "c2", "text": "Traditional bindi or identifying marks are precisely placed and centered."},
            {"id": "c3", "text": "Facial harmony captures the subject's distinctive personal likeness."},
        ],
        "mastery_question": {
            "question": "What is the secret to capturing a true likeness according to Andrew Loomis?",
            "options": [
                "Getting the proportional spacing between bone landmarks exactly right.",
                "Adding more dark lines until it looks like the photo.",
                "Using a soft eraser to blur the drawing.",
            ],
            "correct_index": 0,
            "explanation": "Loomis taught that likeness is not in the surface eyelashes or wrinkles, but in the exact proportional relationships between the underlying bone landmarks.",
        },
    },
    18: {
        "stage": 18,
        "title": "Major Shadow Structures & Value Cross-Hatching",
        "category": "Value & Lighting",
        "pencil_grade": "4B Soft Graphite",
        "stroke_type": "Multi-angle directional cross-hatching and planar shading",
        "estimated_duration_min": 10,
        "learning_objective": "Render classical anatomical shadow planes using multi-angle cross-hatching to create profound 3D depth.",
        "loomis_core_rule": "Value makes form! Separate the light from the shadow with clear terminator lines. Cast shadows under the jaw, nose, and lips anchor the portrait to the paper.",
        "step_by_step_instructions": [
            "Determine the single dominant light direction (e.g., top-left at 45 degrees).",
            "Hatch the under-jaw cast shadow across the neck cylinder with parallel strokes matching the light angle.",
            "Cross-hatch at -40 degrees directly under the mandibular rim to build deep, rich graphite density.",
            "Hatch the orbital socket hollows under the brow ridge to recess the eye globes.",
            "Drop the triangular cast shadow beneath the nose columella onto the upper lip philtrum.",
            "Shade the downward-sloping upper lip cushions and the crescent labiomental groove below the lower lip.",
        ],
        "pro_tips": [
            "Keep your hatching strokes parallel and consistent in rhythm—haphazard scribbling destroys form.",
            "Shadows should be transparent: you should always be able to feel the underlying construction through the graphite tone.",
        ],
        "common_pitfalls": [
            "Smudging shadows with your bare finger (oils from skin ruin the graphite tooth of the paper).",
            "Using multiple conflicting light source directions.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Under-jaw cast shadow on neck cylinder features rich dual-angle cross-hatching."},
            {"id": "c2", "text": "Orbital eye sockets and subnasale shadow planes are clearly modeled."},
            {"id": "c3", "text": "Upper lip and labiomental groove are shaded in harmonious tonal values."},
        ],
        "mastery_question": {
            "question": "Why is cross-hatching superior to solid flat black fill for anatomical shadows?",
            "options": [
                "Because cross-hatching preserves the luminous tooth of the paper and creates atmospheric depth.",
                "Because cross-hatching takes less pencil lead.",
                "Because pencils cannot draw solid black.",
            ],
            "correct_index": 0,
            "explanation": "Cross-hatching allows tiny specks of the white paper to show through, creating an atmospheric, luminous, and authentic graphite drawing feel.",
        },
    },
    19: {
        "stage": 19,
        "title": "Secondary Details, Saree Drapery & Textures",
        "category": "Details & Textures",
        "pencil_grade": "3B / 5B Velvet Graphite",
        "stroke_type": "Flowing fabric folds, jewelry filigree, and flyaway wisps",
        "estimated_duration_min": 10,
        "learning_objective": "Render fine secondary details: delicate eyelash accents, fabric drapery folds, jewelry ornamentation, and organic hair strands.",
        "loomis_core_rule": "Secondary details must never overwhelm primary forms. Add the rhythmic drapery folds, flyaway curls, and jewelry accents as graceful embroidery upon the solid anatomical masses.",
        "step_by_step_instructions": [
            "Add delicate eyelash flick accents at the outer corners of the eyes.",
            "Render the rhythmic drapery folds of the saree pallu curving across the cylindrical shoulder volume.",
            "Detail the choker necklace with ornate filigree beads and dangling pearl drops.",
            "Stroke fine flyaway temple wisps and organic curls escaping from the hair bun.",
        ],
        "pro_tips": [
            "Draw fabric folds in rhythmic pipe and diaper patterns, draping over the forms beneath.",
            "Keep jewelry crisp with tiny sharp graphite points, contrasting against soft skin tones.",
        ],
        "common_pitfalls": [
            "Over-detailing secondary fabric patterns until the face loses its focal dominance.",
            "Drawing stiff, wire-like eyelashes that stick straight out.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Eyelash accents are delicate and curve naturally outward."},
            {"id": "c2", "text": "Saree drapery folds follow the cylindrical volume of shoulders and chest."},
            {"id": "c3", "text": "Jewelry and hair textures enrich the drawing without distracting from the face."},
        ],
        "mastery_question": {
            "question": "What is the primary rule for rendering fabric drapery over the body?",
            "options": [
                "Folds must wrap over and reveal the underlying anatomical cylinders and masses.",
                "Fabric should be drawn flat without regard to the body beneath.",
                "Folds should always be straight vertical lines.",
            ],
            "correct_index": 0,
            "explanation": "Andrew Loomis emphasizes that clothing drapery always conforms to and reveals the cylindrical volumes of the neck, torso, and limbs underneath.",
        },
    },
    20: {
        "stage": 20,
        "title": "Final Masterpiece Synthesis & Atelier Finish",
        "category": "Masterpiece Finish",
        "pencil_grade": "6B Deep Velvet Charcoal & Graphite",
        "stroke_type": "Deep value accents, luminous eraser lifts, and cursive signature",
        "estimated_duration_min": 12,
        "learning_objective": "Synthesize the entire drawing: balance whispering underdrawing scaffolding, deep 6B graphite values, pure luminous highlights, and artist signature.",
        "loomis_core_rule": "The master portrait is a symphony of construction and tone. The geometric scaffolding whispers beneath the surface; the rich graphite values sing; the luminous highlights sparkle. Sign your work with pride.",
        "step_by_step_instructions": [
            "Ensure the initial 2H Loomis scaffolding faintly whispers through the drawing to reveal its classical construction pedigree.",
            "Punch in deep 6B graphite dark accents in the pupils, inner hair bun core, and the under-jaw terminator.",
            "Use a kneaded eraser to lift pure luminous specular catchlights on the pupils, the apex of the nose tip, and the lower lip cushion.",
            "Check the full tonal scale from paper white (catchlights) to deep 6B velvet graphite (pupils).",
            "Sign your masterpiece in cursive pencil in the lower right corner with an elegant underline flourish.",
        ],
        "pro_tips": [
            "Step back 6 feet and do the squint test: the portrait should feel three-dimensional, alive, and breathing.",
            "Spray with workable matte fixative from 12 inches away to preserve your graphite work permanently.",
        ],
        "common_pitfalls": [
            "Completely erasing the Loomis scaffolding: master atelier drawings celebrate the structural lines!",
            "Over-working the drawing until the paper tooth is crushed and shines with a gray metallic glare.",
        ],
        "checkpoint_checklist": [
            {"id": "c1", "text": "Whispering Loomis underdrawing scaffolding is subtly visible beneath the drawing."},
            {"id": "c2", "text": "Luminous eraser-lift highlights shine on pupils, nose tip, and lower lip."},
            {"id": "c3", "text": "Atelier signature and flourish are proudly inscribed on archival paper."},
        ],
        "mastery_question": {
            "question": "Why do classical master portrait drawings leave faint construction lines visible?",
            "options": [
                "Because visible scaffolding reveals the intellectual anatomical mastery and gives the drawing structural life.",
                "Because artists ran out of erasers.",
                "Because pencil lines cannot be erased from cold-pressed paper.",
            ],
            "correct_index": 0,
            "explanation": "Classical masters from Leonardo da Vinci to Andrew Loomis left construction lines visible because they celebrate the architecture of the human head.",
        },
    },
}


def get_stage_curriculum(stage_num: int) -> Optional[Dict[str, Any]]:
    """Returns the detailed lesson curriculum for a given stage (1–20)."""
    return LESSON_CURRICULUM.get(stage_num)


def verify_stage_checkpoint(
    stage_num: int,
    checks: List[bool],
    notes: str = "",
) -> Dict[str, Any]:
    """
    Evaluates a student's self-assessment checklist for a stage.
    Returns:
      - score_percent: int (0 to 100)
      - mastery_level: "Needs Practice" | "Proficient" | "Mastered"
      - can_advance: bool
      - feedback: str
      - next_stage: int
    """
    curriculum = get_stage_curriculum(stage_num)
    if not curriculum:
        return {
            "error": f"Invalid stage number {stage_num}. Must be between 1 and 20.",
            "can_advance": False,
        }

    total_checks = len(curriculum["checkpoint_checklist"])
    completed_checks = sum(1 for c in checks if c)
    score_percent = int(round((completed_checks / max(1, total_checks)) * 100))

    if completed_checks == total_checks:
        mastery_level = "Mastered"
        can_advance = True
        feedback = f"Outstanding! You have mastered Stage {stage_num} ({curriculum['title']}). Your anatomical construction adheres to Andrew Loomis's core principles. Proceed to Stage {min(20, stage_num + 1)}!"
    elif completed_checks >= 2:
        mastery_level = "Proficient"
        can_advance = True
        feedback = f"Great work! You have verified major criteria for Stage {stage_num}. Refine the remaining checkpoint to solidify your craftsmanship, then proceed."
    else:
        mastery_level = "Needs Practice"
        can_advance = False
        feedback = f"Keep practicing Stage {stage_num}. Review the common pitfalls and pro tips. Verify at least 2 checkpoints before advancing to preserve solid anatomical foundations."

    return {
        "stage": stage_num,
        "title": curriculum["title"],
        "category": curriculum["category"],
        "score_percent": score_percent,
        "completed_count": completed_checks,
        "total_count": total_checks,
        "mastery_level": mastery_level,
        "can_advance": can_advance,
        "next_stage": min(20, stage_num + 1),
        "feedback": feedback,
        "pro_tip": curriculum["pro_tips"][0] if curriculum.get("pro_tips") else "",
    }
