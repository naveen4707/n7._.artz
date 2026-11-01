/**
 * LOOMIS AI STUDIO — CLIENT CONTROLLER
 * Full interactive 20-stage Andrew Loomis portrait drawing studio
 */

(function () {
  'use strict';

  // ── APP STATE ─────────────────────────────────────────────────────────
  const state = {
    currentStage: 20,
    currentJobId: 'reference_job',
    stages: [],
    viewMode: 'drawing',
    isPlaying: false,
    playInterval: null,
    playSpeed: 1000,
    photoUrl: '/input/reference.jpg',
    bwPhotoUrl: '/input/reference_bw.jpg',
    referenceMode: 'bw',
    selectedFile: null,
    curriculum: {},
    checkpoints: JSON.parse(localStorage.getItem('loomis_checkpoints') || '{}'),
    telemetry: {
      yaw: '-1.2°',
      pitch: '+2.5°',
      roll: '+0.8°',
      landmarks: 478,
      shadowAngle: '-30° Left',
      specialMarks: 'Forehead Bindi',
    },
  };

  // ── DOM ELEMENTS ───────────────────────────────────────────────────────
  const els = {
    // Mode tabs
    modeTabs: document.querySelectorAll('.mode-tab'),
    views: {
      drawing: document.getElementById('viewDrawing'),
      split: document.getElementById('viewSplit'),
      sidebyside: document.getElementById('viewSideBySide'),
      onion: document.getElementById('viewOnion'),
      grid: document.getElementById('viewGrid'),
    },
    // Reference Mode Toggles
    btnRefBW: document.getElementById('btnRefBW'),
    btnRefColor: document.getElementById('btnRefColor'),
    // Images
    mainDrawingImg: document.getElementById('mainDrawingImg'),
    splitPhotoImg: document.getElementById('splitPhotoImg'),
    splitDrawingImg: document.getElementById('splitDrawingImg'),
    sidePhotoImg: document.getElementById('sidePhotoImg'),
    sideDrawingImg: document.getElementById('sideDrawingImg'),
    onionPhotoImg: document.getElementById('onionPhotoImg'),
    onionDrawingImg: document.getElementById('onionDrawingImg'),
    // Split elements
    splitContainer: document.getElementById('splitContainer'),
    splitDrawingLayer: document.getElementById('splitDrawingLayer'),
    splitHandle: document.getElementById('splitHandle'),
    // Onion slider
    onionSlider: document.getElementById('onionSlider'),
    onionValue: document.getElementById('onionValue'),
    // Playback
    btnPrevStage: document.getElementById('btnPrevStage'),
    btnNextStage: document.getElementById('btnNextStage'),
    btnPlayPause: document.getElementById('btnPlayPause'),
    playIcon: document.getElementById('playIcon'),
    pauseIcon: document.getElementById('pauseIcon'),
    selSpeed: document.getElementById('selSpeed'),
    stageSlider: document.getElementById('stageSlider'),
    scrubCurrentNum: document.getElementById('scrubCurrentNum'),
    scrubTitle: document.getElementById('scrubTitle'),
    stageDotsGrid: document.getElementById('stageDotsGrid'),
    // Sidebar Hero
    badgeCategory: document.getElementById('badgeCategory'),
    badgePencilText: document.getElementById('badgePencilText'),
    heroStageNumber: document.getElementById('heroStageNumber'),
    heroStageTitle: document.getElementById('heroStageTitle'),
    loomisPrinciple: document.getElementById('loomisPrinciple'),
    drawingAction: document.getElementById('drawingAction'),
    // Telemetry
    tPerspective: document.getElementById('tPerspective'),
    tEyeState: document.getElementById('tEyeState'),
    tYaw: document.getElementById('tYaw'),
    tPitch: document.getElementById('tPitch'),
    tRoll: document.getElementById('tRoll'),
    tLight: document.getElementById('tLight'),
    tMarks: document.getElementById('tMarks'),
    // Header actions
    btnOpenUpload: document.getElementById('btnOpenUpload'),
    btnDownloadCurrent: document.getElementById('btnDownloadCurrent'),
    btnDownloadZip: document.getElementById('btnDownloadZip'),
    downloadStageNum: document.getElementById('downloadStageNum'),
    engineStatusText: document.getElementById('engineStatusText'),
    // Grid container
    stagesGridContainer: document.getElementById('stagesGridContainer'),
    // Validation elements
    valScoreBadge: document.getElementById('valScoreBadge'),
    valThirdsDev: document.getElementById('valThirdsDev'),
    segUpper: document.getElementById('segUpper'),
    segMid: document.getElementById('segMid'),
    segLower: document.getElementById('segLower'),
    valInterocular: document.getElementById('valInterocular'),
    valPlaneTilt: document.getElementById('valPlaneTilt'),
    valRecText: document.getElementById('valRecText'),
    // Presets
    presetsList: document.getElementById('presetsList'),
    // Loader overlay
    pipelineLoader: document.getElementById('pipelineLoader'),
    loaderTitle: document.getElementById('loaderTitle'),
    loaderSubtitle: document.getElementById('loaderSubtitle'),
    progressBarFill: document.getElementById('progressBarFill'),
    loaderLog: document.getElementById('loaderLog'),
    // Upload modal
    uploadModal: document.getElementById('uploadModal'),
    btnCloseUpload: document.getElementById('btnCloseUpload'),
    btnCancelUpload: document.getElementById('btnCancelUpload'),
    dropzone: document.getElementById('dropzone'),
    fileInput: document.getElementById('fileInput'),
    btnBrowse: document.getElementById('btnBrowse'),
    dropzonePreview: document.getElementById('dropzonePreview'),
    previewImg: document.getElementById('previewImg'),
    previewBwImg: document.getElementById('previewBwImg'),
    previewBwSpinner: document.getElementById('previewBwSpinner'),
    previewBwStatus: document.getElementById('previewBwStatus'),
    previewFilename: document.getElementById('previewFilename'),
    btnRemoveFile: document.getElementById('btnRemoveFile'),
    btnStartProcessing: document.getElementById('btnStartProcessing'),
    // Canvas quick tools
    chkPaperTooth: document.getElementById('chkPaperTooth'),
    btnZoomReset: document.getElementById('btnZoomReset'),
    btnFullscreen: document.getElementById('btnFullscreen'),
    canvasViewport: document.getElementById('canvasViewport'),
    // AI Art Coach elements
    coachSpeechBubble: document.getElementById('coachSpeechBubble'),
    btnCoachProportions: document.getElementById('btnCoachProportions'),
    btnCoachTechnique: document.getElementById('btnCoachTechnique'),
    btnCoachMistakes: document.getElementById('btnCoachMistakes'),
    btnCoachPencil: document.getElementById('btnCoachPencil'),
    // Interactive Student Practice Checkpoint elements
    checkpointCard: document.getElementById('checkpointCard'),
    checkpointStageBadge: document.getElementById('checkpointStageBadge'),
    masteryBadge: document.getElementById('masteryBadge'),
    checkpointScoreText: document.getElementById('checkpointScoreText'),
    checkpointProgressFill: document.getElementById('checkpointProgressFill'),
    checkpointChecklist: document.getElementById('checkpointChecklist'),
    checkpointProtipText: document.getElementById('checkpointProtipText'),
    btnVerifyCheckpoint: document.getElementById('btnVerifyCheckpoint'),
  };

  // ── INITIALIZATION ────────────────────────────────────────────────────
  async function init() {
    setupEventListeners();
    await fetchStages();
    await fetchCurriculum();
    await fetchPresets();
    await fetchValidation();
    checkEngineStatus();
    renderStageDots();
    renderStagesGrid();
    updateReferenceImages();
    setStage(20);
  }

  // ── API CALLS ─────────────────────────────────────────────────────────
  async function fetchStages() {
    try {
      const res = await fetch('/api/stages-info');
      const data = await res.json();
      if (data && data.stages) {
        state.stages = data.stages;
      }
    } catch (err) {
      console.warn('Could not fetch stage metadata, using fallback:', err);
    }
  }

  async function fetchCurriculum() {
    try {
      const res = await fetch('/api/lesson/curriculum');
      const data = await res.json();
      if (data && data.stages) {
        state.curriculum = data.stages;
      }
    } catch (err) {
      console.warn('Could not fetch lesson curriculum:', err);
    }
  }

  async function fetchValidation() {
    try {
      const res = await fetch('/api/validation');
      const data = await res.json();
      if (data && data.version) {
        updateValidationUI(data);
      }
    } catch (err) {
      console.warn('Could not fetch validation report:', err);
    }
  }

  async function fetchPresets() {
    try {
      const res = await fetch('/api/presets');
      const data = await res.json();
      if (data && data.presets && data.presets.length > 0) {
        renderPresets(data.presets);
      }
    } catch (err) {
      console.warn('Could not fetch presets:', err);
    }
  }

  async function checkEngineStatus() {
    try {
      const res = await fetch('/api/status');
      const data = await res.json();
      if (data && data.status === 'online') {
        els.engineStatusText.textContent = 'AI Engine Ready • 20 Stages Synchronized';
      }
    } catch (err) {
      els.engineStatusText.textContent = 'Engine Offline • Using Local Cache';
    }
  }

  // ── STAGE 0 DEFINITION ───────────────────────────────────────────────
  const STAGE_0_INFO = {
    stage: 0,
    title: "Black & White Photo Reference",
    category: "Photographic Tonal Study",
    pencil: "Photo Chiaroscuro Values",
    loomisPrinciple: "Before touching pencil to paper, convert the portrait into high-contrast black and white to isolate true values and lighting planes free of color distraction.",
    drawingAction: "Observe the 5 key values: highlight, midtone, core shadow, reflected light, and cast shadow.",
  };

  // ── RENDER STAGE DOTS (0 TO 20) ───────────────────────────────────────
  function renderStageDots() {
    els.stageDotsGrid.innerHTML = '';
    for (let i = 0; i <= 20; i++) {
      const dot = document.createElement('button');
      dot.className = `stage-dot ${i === state.currentStage ? 'active' : ''} ${i === 0 ? 'stage-dot-zero' : ''}`;
      dot.textContent = i === 0 ? '◐ 0' : i;
      dot.title = `Stage ${i}: ${getStageInfo(i).title}`;
      dot.addEventListener('click', () => {
        pausePlayback();
        setStage(i);
      });
      els.stageDotsGrid.appendChild(dot);
    }
  }

  function getStageInfo(num) {
    if (num === 0) {
      return STAGE_0_INFO;
    }
    if (state.stages && state.stages.length >= num) {
      return state.stages[num - 1];
    }
    return {
      stage: num,
      title: `Stage ${num}`,
      category: num <= 7 ? 'Loomis Foundation' : num <= 14 ? 'Anatomical Features' : 'Photo-Accurate Finish',
      pencil: num <= 7 ? '2H Hard Graphite' : '2B Soft Graphite',
      loomisPrinciple: 'Structural drawing requires adherence to 3D form and perspective.',
      drawingAction: 'Follow the guidelines to sketch the contours on paper.',
    };
  }

  const COACH_TIPS = {
    0: {
      proportions: "Converting the photo into black and white is the secret of classical portrait masters. It removes color deception and displays the true value hierarchy.",
      technique: "Squint your eyes to blur details and spot the large light and shadow masses on the face.",
      mistakes: "Jumping into line drawing while looking at color photos. Color temperatures distract from accurate 3D values.",
      pencils: "Value scale 1 (Paper White) through 9 (6B Deep Velvet Charcoal)."
    },
    1: {
      proportions: "The cranium sphere forms 2/3 of total head volume. Keep this sphere light (4H); everything hangs from it.",
      technique: "Draw from your shoulder with light ghosting passes. Keep strokes loose and circular.",
      mistakes: "Drawing an egg or oval instead of a true sphere. Skull sides will be flattened later.",
      pencils: "4H or 2H Hard Graphite. Feather-light pressure; never groove the paper tooth."
    },
    2: {
      proportions: "The brow line is the sphere's equator. The vertical line marks facial 3D symmetry.",
      technique: "Curve lines across the spherical contour like longitude and latitude on a globe.",
      mistakes: "Drawing the centerline flat. Follow 3D perspective following head tilt.",
      pencils: "4H Graphite with crisp, deliberate lines."
    },
    3: {
      proportions: "Side plane disc height is roughly 2/3 of sphere height where ears attach.",
      technique: "Slice off the cranial side disc. The top marks hairline, the bottom marks nose base.",
      mistakes: "Placing the side disc too far forward toward the eyes.",
      pencils: "2H Graphite for clean geometric landmarks."
    },
    4: {
      proportions: "The jaw drops from the side disc center and swings into perspective to the chin.",
      technique: "Draw sweeping lines from temples down to gonial angle and join at chin wedge.",
      mistakes: "Making the jaw too pointy or detaching it from the side disc axis.",
      pencils: "2H Graphite with rhythmic, confident strokes."
    },
    5: {
      proportions: "Rule of Thirds: Hairline to brow, brow to nose base, nose base to chin are equal.",
      technique: "Mark the nasal septum keystone at precisely 1/3 division along facial axis.",
      mistakes: "Placing nose base too low, causing elongated midface.",
      pencils: "H or HB Graphite for structural keypoints."
    },
    6: {
      proportions: "The mouth sits on a cylindrical muzzle wrapping across facial curvature.",
      technique: "Place oral fissure 1/3 down from nose base to chin, tucking corners back in perspective.",
      mistakes: "Drawing lips as flat horizontal stickers across a 3D cylinder.",
      pencils: "H Graphite with curved directional strokes."
    },
    7: {
      proportions: "All planes of the head are now unified in 3D perspective.",
      technique: "Step back 6 feet or view your drawing in a mirror to verify tilt and proportions.",
      mistakes: "Starting facial details before checking cranial perspective.",
      pencils: "HB Medium Graphite to lock down the master armature."
    },
    8: {
      proportions: "Orbital eye sockets are deep bony cavities under the brow shelf.",
      technique: "Block in the almond contour of sclera resting deep inside the socket cavity.",
      mistakes: "Drawing eye outlines on the surface without socket depth.",
      pencils: "HB Graphite with diagonal socket cross-hatching."
    },
    9: {
      proportions: "Eyelids wrap over the spherical eyeball. Upper lid overlaps lower at outer canthus.",
      technique: "Carve the dark pupil core, leave a crisp specular highlight, and define eyelid folds.",
      mistakes: "Solid black eye outline without specular highlights or eyelid thickness.",
      pencils: "2B Soft Graphite for dark pupil core; kneaded eraser for highlight."
    },
    10: {
      proportions: "Brows follow the bone shelf: thick at glabella, arching at iris, tapering at temple.",
      technique: "Stroke in the natural direction of hair growth along superciliary ridge.",
      mistakes: "Solid black blocks. Draw rhythmic clusters over bone.",
      pencils: "B or 2B Graphite with flicking strokes."
    },
    11: {
      proportions: "The nose is a 4-plane wedge: bridge, two sloping side planes, undercut ball tip.",
      technique: "Refine alar wings, infratip lobule, and dark crescent nostrils softly inside shadow.",
      mistakes: "Outlining the nose bridge with harsh lines instead of soft plane breaks.",
      pencils: "B for bridge structure, 2B for nostrils and alar groove."
    },
    12: {
      proportions: "Upper lip has 3 nodes; lower lip has 2 pillows. Upper lip is in shadow.",
      technique: "Sculpt Cupid's bow, vermilion border, and oral fissure corners.",
      mistakes: "Hard outline around bottom lip. Lower lip is defined by shadow beneath it!",
      pencils: "2B Soft Graphite with soft edge gradation."
    },
    13: {
      proportions: "Cheekbones catch high light; temporal crest defines front face plane.",
      technique: "Trace subtle transitions along zygomatic arch down to chin.",
      mistakes: "Harsh cheek lines. Blend subtly into skin tone.",
      pencils: "HB Graphite with gentle circular shading."
    },
    14: {
      proportions: "Ears align vertically between brow line and nose base.",
      technique: "Construct outer helix rim, inner Y antihelix, concha bowl, and earlobes.",
      mistakes: "Placing ears too high or detached from side plane axis.",
      pencils: "HB Graphite with clean anatomical contours."
    },
    15: {
      proportions: "Hair sits ABOVE the cranial sphere with volume (not flat on skull).",
      technique: "Block in big silhouette shapes and crown volume before individual strands.",
      mistakes: "Drawing thousands of thin wires. Treat hair like sculptural volume!",
      pencils: "2B and 4B Soft Graphite for mass volume and deep darks."
    },
    16: {
      proportions: "Neck is a forward-tilted cylinder flanked by sternocleidomastoid muscles.",
      technique: "Construct neck cylinder and draw collar, necklace, and shoulder drape contours.",
      mistakes: "Drawing vertical straight lines for the neck.",
      pencils: "2B Graphite with rhythmic flowing strokes."
    },
    17: {
      proportions: "Refine authentic contours and distinct personal facial character.",
      technique: "Refine subtle facial contours and render authentic identifying marks.",
      mistakes: "Over-darkening peripheral contours, which flattens 3D form.",
      pencils: "3B Soft Graphite."
    },
    18: {
      proportions: "Separate light and shadow with clear terminator line.",
      technique: "Cross-hatch under-chin cast shadow angled to match the subject's lighting.",
      mistakes: "Inconsistent shading angles. Keep hatching unified in perspective.",
      pencils: "4B Soft Graphite for rich, velvety shadow plane."
    },
    19: {
      proportions: "Secondary details: fabric weave, jewelry facets, and escaping hair wisps.",
      technique: "Add rhythmic drapery folds, tendrils, and fine ornamental accents.",
      mistakes: "Over-detailing areas outside the focal portrait center.",
      pencils: "3B / 5B Velvet Graphite."
    },
    20: {
      proportions: "Masterpiece synthesis: subtle geometric scaffolding whispers beneath final portrait.",
      technique: "Final balance: lift specular highlights on nose and lips with kneaded eraser.",
      mistakes: "Erasing all construction lines. Master drawings celebrate visible scaffolding!",
      pencils: "6B Deep Velvet Charcoal & Graphite for profound depth."
    }
  };

  // ── SET CURRENT STAGE ─────────────────────────────────────────────────
  function setStage(stageNum) {
    stageNum = Math.max(0, Math.min(20, stageNum));
    state.currentStage = stageNum;

    const info = getStageInfo(stageNum);
    let drawingUrl;
    if (stageNum === 0) {
      drawingUrl = state.bwPhotoUrl || '/input/reference_bw.jpg';
    } else {
      const stagePad = String(stageNum).padStart(2, '0');
      drawingUrl = `/output/hand_drawn/stage_${stagePad}.png?v=${Date.now().toString().slice(0, 8)}`;
    }

    // Update images
    els.mainDrawingImg.src = drawingUrl;
    els.splitDrawingImg.src = drawingUrl;
    els.sideDrawingImg.src = drawingUrl;
    els.onionDrawingImg.src = drawingUrl;

    // Update controls
    els.stageSlider.value = stageNum;
    els.scrubCurrentNum.textContent = stageNum === 0 ? '0 (B&W Ref)' : stageNum;
    els.scrubTitle.textContent = info.title;
    els.downloadStageNum.textContent = stageNum;

    // Update Stage Dots
    const dots = els.stageDotsGrid.querySelectorAll('.stage-dot');
    dots.forEach((dot, idx) => {
      dot.classList.toggle('active', idx === stageNum);
    });

    // Update Sidebar
    els.heroStageNumber.textContent = stageNum === 0 ? `STEP 00 / 20` : `STAGE ${stageNum} / 20`;
    els.heroStageTitle.textContent = info.title;
    els.badgeCategory.textContent = info.category || 'Loomis Method';
    els.badgePencilText.textContent = info.pencil || 'HB Graphite';
    els.loomisPrinciple.textContent = `"${info.loomisPrinciple || 'Observe the true form.'}"`;
    els.drawingAction.textContent = info.drawingAction || 'Construct with light graphite strokes.';

    // Update AI Coach speech bubble with stage advice
    if (els.coachSpeechBubble && COACH_TIPS[stageNum]) {
      els.coachSpeechBubble.textContent = `Stage ${stageNum} Advice: ${COACH_TIPS[stageNum].technique}`;
    }

    // Side by side label
    const sideStageNum = document.querySelector('.sideStageNum');
    if (sideStageNum) sideStageNum.textContent = stageNum === 0 ? 'B&W Ref' : stageNum;

    // Render interactive practice checkpoint rubric for this stage
    renderCheckpointRubric(stageNum);
  }

  // ── INTERACTIVE DRAWING CHECKPOINT & PRACTICE RUBRIC ──────────────────
  function renderCheckpointRubric(stageNum) {
    if (!els.checkpointCard) return;
    if (stageNum === 0) {
      els.checkpointCard.style.display = 'none';
      return;
    }
    els.checkpointCard.style.display = 'block';

    const curr = (state.curriculum && state.curriculum[stageNum]) || null;
    if (els.checkpointStageBadge) {
      els.checkpointStageBadge.textContent = `Stage ${stageNum}`;
    }

    if (!state.checkpoints[stageNum]) {
      state.checkpoints[stageNum] = [false, false, false];
    }
    const stageChecks = state.checkpoints[stageNum];

    // Checklist items
    if (els.checkpointChecklist) {
      els.checkpointChecklist.innerHTML = '';
      const checklistItems = (curr && curr.checkpoint_checklist && curr.checkpoint_checklist.length === 3)
        ? curr.checkpoint_checklist
        : [
            { id: 'c1', text: 'Geometric landmarks accurately aligned in 3D perspective.' },
            { id: 'c2', text: 'Pencil pressure matches recommended graphite hardness.' },
            { id: 'c3', text: 'Proportions verified with Andrew Loomis sighting rules.' }
          ];

      checklistItems.forEach((item, idx) => {
        const isChecked = Boolean(stageChecks[idx]);
        const itemEl = document.createElement('div');
        itemEl.className = `checkpoint-item ${isChecked ? 'checked' : ''}`;
        itemEl.dataset.index = idx;
        itemEl.innerHTML = `
          <div class="checkpoint-checkbox">${isChecked ? '✓' : ''}</div>
          <div class="checkpoint-item-text">${item.text}</div>
        `;

        itemEl.addEventListener('click', () => {
          toggleCheckpointItem(stageNum, idx);
        });

        els.checkpointChecklist.appendChild(itemEl);
      });
    }

    // Studio Pro Tip
    if (els.checkpointProtipText) {
      const tip = (curr && curr.pro_tips && curr.pro_tips[0]) || 'Step back 4 feet to verify balance.';
      els.checkpointProtipText.textContent = tip;
    }

    updateCheckpointProgress(stageNum);
  }

  function toggleCheckpointItem(stageNum, idx) {
    if (!state.checkpoints[stageNum]) {
      state.checkpoints[stageNum] = [false, false, false];
    }
    state.checkpoints[stageNum][idx] = !state.checkpoints[stageNum][idx];
    try {
      localStorage.setItem('loomis_checkpoints', JSON.stringify(state.checkpoints));
    } catch (e) {}

    renderCheckpointRubric(stageNum);
  }

  function updateCheckpointProgress(stageNum) {
    const checks = state.checkpoints[stageNum] || [false, false, false];
    const completed = checks.filter(Boolean).length;
    const total = 3;
    const pct = Math.round((completed / total) * 100);

    if (els.checkpointScoreText) {
      els.checkpointScoreText.textContent = `${completed} of ${total} Criteria Met (${pct}%)`;
    }
    if (els.checkpointProgressFill) {
      els.checkpointProgressFill.style.width = `${pct}%`;
    }

    if (els.masteryBadge) {
      if (completed === total) {
        els.masteryBadge.textContent = 'Mastered';
        els.masteryBadge.className = 'badge-mini badge-mastery mastered';
      } else if (completed >= 2) {
        els.masteryBadge.textContent = 'Proficient';
        els.masteryBadge.className = 'badge-mini badge-mastery';
      } else {
        els.masteryBadge.textContent = 'In Progress';
        els.masteryBadge.className = 'badge-mini badge-mastery';
      }
    }

    if (els.btnVerifyCheckpoint) {
      els.btnVerifyCheckpoint.disabled = completed < 2;
    }
  }

  async function handleVerifyCheckpoint() {
    const stageNum = state.currentStage;
    const checks = state.checkpoints[stageNum] || [false, false, false];
    try {
      const res = await fetch('/api/lesson/verify-checkpoint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          stage: stageNum,
          checks: checks,
        }),
      });
      const data = await res.json();
      if (data && data.feedback) {
        if (els.coachSpeechBubble) {
          els.coachSpeechBubble.textContent = `✓ ${data.feedback}`;
        }
        if (data.can_advance && stageNum < 20) {
          setTimeout(() => {
            setStage(stageNum + 1);
          }, 800);
        }
      }
    } catch (err) {
      console.warn('Verify checkpoint failed:', err);
      if (stageNum < 20) {
        setStage(stageNum + 1);
      }
    }
  }

  // ── PLAYBACK LOGIC ────────────────────────────────────────────────────
  function togglePlayPause() {
    if (state.isPlaying) {
      pausePlayback();
    } else {
      startPlayback();
    }
  }

  function startPlayback() {
    state.isPlaying = true;
    els.playIcon.classList.add('hidden');
    els.pauseIcon.classList.remove('hidden');

    if (state.currentStage >= 20) {
      setStage(0);
    }

    clearInterval(state.playInterval);
    state.playInterval = setInterval(() => {
      if (state.currentStage < 20) {
        setStage(state.currentStage + 1);
      } else {
        pausePlayback();
      }
    }, state.playSpeed);
  }

  function pausePlayback() {
    state.isPlaying = false;
    els.playIcon.classList.remove('hidden');
    els.pauseIcon.classList.add('hidden');
    clearInterval(state.playInterval);
  }

  // ── REFERENCE MODE (B&W vs COLOR) ──────────────────────────────────────
  function updateReferenceImages() {
    const targetUrl = state.referenceMode === 'bw'
      ? (state.bwPhotoUrl || state.photoUrl)
      : state.photoUrl;

    if (els.splitPhotoImg) els.splitPhotoImg.src = targetUrl;
    if (els.sidePhotoImg) els.sidePhotoImg.src = targetUrl;
    if (els.onionPhotoImg) els.onionPhotoImg.src = targetUrl;

    if (els.btnRefBW) els.btnRefBW.classList.toggle('active', state.referenceMode === 'bw');
    if (els.btnRefColor) els.btnRefColor.classList.toggle('active', state.referenceMode === 'color');
  }

  function setReferenceMode(mode) {
    state.referenceMode = mode;
    updateReferenceImages();
  }

  // ── VIEW MODE SWITCHING ───────────────────────────────────────────────
  function setViewMode(mode) {
    state.viewMode = mode;
    els.modeTabs.forEach(tab => {
      tab.classList.toggle('active', tab.dataset.mode === mode);
    });

    Object.entries(els.views).forEach(([key, viewEl]) => {
      if (viewEl) {
        viewEl.classList.toggle('active', key === mode);
      }
    });

    if (mode === 'grid') {
      renderStagesGrid();
    }

    // Reset split slider to 50% on entering split mode
    if (mode === 'split') {
      updateSplit(50);
    }
  }

  function renderStagesGrid() {
    if (!els.stagesGridContainer) return;
    els.stagesGridContainer.innerHTML = '';

    // Step 0 card: Black & White Photo Reference
    const zeroCard = document.createElement('div');
    zeroCard.className = `stage-grid-card ${state.currentStage === 0 ? 'active-stage' : ''}`;
    const zeroImgSrc = state.bwPhotoUrl || '/input/reference_bw.jpg';
    zeroCard.innerHTML = `
      <div class="stage-grid-thumb">
        <img src="${zeroImgSrc}" alt="Black & White Photo Reference" loading="lazy">
      </div>
      <div class="stage-grid-info">
        <span class="stage-grid-num">STEP 00</span>
        <div class="stage-grid-title" title="Black & White Photo Reference">B&W Photo Reference</div>
        <span class="stage-grid-pencil">Tonal Chiaroscuro</span>
      </div>
    `;
    zeroCard.addEventListener('click', () => {
      setStage(0);
      setViewMode('drawing');
    });
    els.stagesGridContainer.appendChild(zeroCard);

    state.stages.forEach(s => {
      const card = document.createElement('div');
      card.className = `stage-grid-card ${s.stage === state.currentStage ? 'active-stage' : ''}`;
      const pad = String(s.stage).padStart(2, '0');
      const imgSrc = s.url || `/output/hand_drawn/stage_${pad}.png`;
      card.innerHTML = `
        <div class="stage-grid-thumb">
          <img src="${imgSrc}" alt="${s.title}" loading="lazy">
        </div>
        <div class="stage-grid-info">
          <span class="stage-grid-num">STAGE ${pad}</span>
          <div class="stage-grid-title" title="${s.title}">${s.title}</div>
          <span class="stage-grid-pencil">${s.pencil || ''}</span>
        </div>
      `;
      card.addEventListener('click', () => {
        setStage(s.stage);
        setViewMode('drawing');
      });
      els.stagesGridContainer.appendChild(card);
    });
  }

  function updateValidationUI(val) {
    if (!val) return;
    if (els.valScoreBadge && val.overall_score !== undefined) {
      els.valScoreBadge.textContent = `${val.overall_score.toFixed(1)}% ${val.status || 'PASS'}`;
      if (val.status === 'WARNING') {
        els.valScoreBadge.style.color = '#f87171';
        els.valScoreBadge.style.borderColor = 'rgba(248, 113, 113, 0.4)';
        els.valScoreBadge.style.background = 'rgba(248, 113, 113, 0.15)';
      } else {
        els.valScoreBadge.style.color = '#34d399';
        els.valScoreBadge.style.borderColor = 'rgba(52, 211, 153, 0.4)';
        els.valScoreBadge.style.background = 'rgba(52, 211, 153, 0.15)';
      }
    }

    const thirdsComp = (val.components || []).find(c => c.name === 'Rule of Thirds');
    if (thirdsComp && thirdsComp.measured_ratios && els.segUpper) {
      const r = thirdsComp.measured_ratios;
      els.segUpper.style.width = `${r.upper_pct}%`;
      els.segUpper.textContent = `${Math.round(r.upper_pct)}%`;
      els.segMid.style.width = `${r.mid_pct}%`;
      els.segMid.textContent = `${Math.round(r.mid_pct)}%`;
      els.segLower.style.width = `${r.lower_pct}%`;
      els.segLower.textContent = `${Math.round(r.lower_pct)}%`;
      if (els.valThirdsDev) els.valThirdsDev.textContent = `${thirdsComp.deviation_percent}% dev`;
    }

    const eyesComp = (val.components || []).find(c => c.name && c.name.includes('Interocular'));
    if (eyesComp && els.valInterocular) {
      els.valInterocular.textContent = `${eyesComp.measured_value}x (${eyesComp.status})`;
    }

    const poseComp = (val.components || []).find(c => c.name && c.name.includes('Pose'));
    if (poseComp && els.valPlaneTilt) {
      els.valPlaneTilt.textContent = `${poseComp.measured_value}° (${poseComp.status})`;
    }

    if (val.recommendations && val.recommendations.length > 0 && els.valRecText) {
      els.valRecText.textContent = val.recommendations[0];
    }
  }

  function downloadZipPackage() {
    const a = document.createElement('a');
    a.href = `/api/jobs/${state.currentJobId}/download-zip`;
    a.download = `loomis_drawing_${state.currentJobId}.zip`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // ── CURTAIN SPLIT SLIDER ──────────────────────────────────────────────
  let isDraggingSplit = false;

  function updateSplit(pct) {
    pct = Math.max(0, Math.min(100, pct));
    els.splitDrawingLayer.style.width = `${pct}%`;
    els.splitHandle.style.left = `${pct}%`;
  }

  function handleSplitDrag(e) {
    if (!isDraggingSplit) return;
    const rect = els.splitContainer.getBoundingClientRect();
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    const x = clientX - rect.left;
    const pct = (x / rect.width) * 100;
    updateSplit(pct);
  }

  // ── PRESETS ───────────────────────────────────────────────────────────
  function renderPresets(presets) {
    els.presetsList.innerHTML = '';
    presets.forEach((p, idx) => {
      const btn = document.createElement('button');
      btn.className = `preset-btn ${idx === 0 ? 'active' : ''}`;
      btn.dataset.filename = p.filename;
      btn.innerHTML = `
        <span class="preset-thumb">&#128105;</span>
        <span class="preset-name">${p.name}</span>
      `;
      btn.addEventListener('click', () => loadPreset(p));
      els.presetsList.appendChild(btn);
    });
  }

  async function loadPreset(preset) {
    document.querySelectorAll('.preset-btn').forEach(b => b.classList.remove('active'));
    const clicked = Array.from(document.querySelectorAll('.preset-btn')).find(b => b.dataset.filename === preset.filename);
    if (clicked) clicked.classList.add('active');

    state.photoUrl = preset.url;
    state.bwPhotoUrl = preset.bwUrl || '/input/reference_bw.jpg';
    updateReferenceImages();

    // Trigger processing
    showLoader('Analyzing Preset Portrait...', 'Generating 20 Andrew Loomis stages');
    updateLoaderProgress(15, 'Running MediaPipe Face Mesh & Head Pose estimation...');

    try {
      const res = await fetch('/api/process-preset', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ filename: preset.filename }),
      });
      const data = await res.json();
      if (data.success) {
        if (data.bwImageUrl) state.bwPhotoUrl = data.bwImageUrl;
        updateReferenceImages();
        updateTelemetry(data.pose);
        setStage(20);
        hideLoader();
      } else {
        alert('Processing failed: ' + (data.error || 'Unknown error'));
        hideLoader();
      }
    } catch (err) {
      console.error(err);
      hideLoader();
    }
  }

  // ── UPLOAD & PROCESSING ───────────────────────────────────────────────
  async function processUploadedImage() {
    if (!state.selectedFile) return;
    const fileToUpload = state.selectedFile;

    closeUploadModal();
    showLoader('Analyzing Uploaded Portrait...', 'Converting to B&W picture & detecting 3D facial geometry');
    updateLoaderProgress(10, 'Step 0: Generating photographic B&W tonal picture...');

    try {
      // Read file to Base64 DataURL
      const reader = new FileReader();
      const base64Promise = new Promise((resolve, reject) => {
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(new Error('Failed to read image file'));
        reader.readAsDataURL(fileToUpload);
      });
      const dataUrl = await base64Promise;

      updateLoaderProgress(25, 'Calculating 478 MediaPipe 3D Landmarks & Head Pose...');

      const ext = fileToUpload.name.split('.').pop() || 'jpg';
      const res = await fetch('/api/process', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: dataUrl,
          filename: fileToUpload.name,
          format: ext,
        }),
      });

      updateLoaderProgress(70, 'Constructing 20 graphite drawing stages...');

      const data = await res.json();
      if (data.success) {
        updateLoaderProgress(100, `Completed in ${data.elapsed_seconds.toFixed(1)} seconds!`);
        setTimeout(async () => {
          hideLoader();
          state.currentJobId = data.job_id || state.currentJobId;
          // Update photo URLs (both color and studio B&W)
          state.photoUrl = data.imageUrl;
          state.bwPhotoUrl = data.bwImageUrl || data.imageUrl;
          updateReferenceImages();

          updateTelemetry(data.pose);
          if (data.validation) {
            updateValidationUI(data.validation);
          }
          await fetchStages();
          renderStagesGrid();
          // Display B&W conversion first (Stage 0), then step through Loomis method!
          setStage(0);
          setTimeout(() => startPlayback(), 1200);
        }, 600);
      } else {
        alert('Processing failed: ' + (data.error || 'Unknown error'));
        hideLoader();
      }
    } catch (err) {
      alert('Error connecting to Loomis AI Engine: ' + err.message);
      hideLoader();
    }
  }

  function updateTelemetry(pose) {
    if (!pose) return;
    if (pose.yaw !== undefined) els.tYaw.textContent = `${pose.yaw > 0 ? '+' : ''}${pose.yaw.toFixed(1)}°`;
    if (pose.pitch !== undefined) els.tPitch.textContent = `${pose.pitch > 0 ? '+' : ''}${pose.pitch.toFixed(1)}°`;
    if (pose.roll !== undefined) els.tRoll.textContent = `${pose.roll > 0 ? '+' : ''}${pose.roll.toFixed(1)}°`;
    if (pose.viewLabel && els.tPerspective) els.tPerspective.textContent = pose.viewLabel;
    if (pose.eyeState && els.tEyeState) els.tEyeState.textContent = pose.eyeState;
  }

  function showLoader(title, subtitle) {
    els.loaderTitle.textContent = title;
    els.loaderSubtitle.textContent = subtitle;
    els.pipelineLoader.classList.remove('hidden');
  }

  function updateLoaderProgress(pct, log) {
    els.progressBarFill.style.width = `${pct}%`;
    if (log) els.loaderLog.textContent = log;
  }

  function hideLoader() {
    els.pipelineLoader.classList.add('hidden');
  }

  // ── MODAL HANDLING ────────────────────────────────────────────────────
  function openUploadModal() {
    els.uploadModal.classList.remove('hidden');
  }

  function closeUploadModal() {
    els.uploadModal.classList.add('hidden');
    resetDropzone();
  }

  function resetDropzone() {
    state.selectedFile = null;
    els.fileInput.value = '';
    els.dropzone.classList.remove('dragover');
    els.dropzonePreview.classList.add('hidden');
    if (els.previewImg) els.previewImg.src = '';
    if (els.previewBwImg) els.previewBwImg.src = '';
    if (els.previewBwSpinner) els.previewBwSpinner.classList.add('hidden');
    document.querySelector('.dropzone-content').classList.remove('hidden');
    els.btnStartProcessing.disabled = true;
  }

  function handleFileSelected(file) {
    if (!file || !file.type.startsWith('image/')) {
      alert('Please select a valid image file (JPG, PNG, WEBP).');
      return;
    }
    state.selectedFile = file;
    const reader = new FileReader();
    reader.onload = async e => {
      const dataUrl = e.target.result;
      els.previewImg.src = dataUrl;
      els.previewFilename.textContent = file.name;
      document.querySelector('.dropzone-content').classList.add('hidden');
      els.dropzonePreview.classList.remove('hidden');
      els.btnStartProcessing.disabled = false;

      // Automatically convert to high-contrast photographic B&W picture for instant preview
      if (els.previewBwSpinner) els.previewBwSpinner.classList.remove('hidden');
      if (els.previewBwStatus) els.previewBwStatus.textContent = 'Converting to photographic B&W picture...';

      try {
        const res = await fetch('/api/convert-bw', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ image: dataUrl, filename: file.name }),
        });
        const bwData = await res.json();
        if (bwData.success && els.previewBwImg) {
          els.previewBwImg.src = bwData.bwImageUrl;
          state.bwPhotoUrl = bwData.bwImageUrl;
          if (els.previewBwStatus) {
            els.previewBwStatus.textContent = '✓ Photographic Tonal B&W Converted • Ready for Loomis Analysis';
          }
        }
      } catch (err) {
        console.warn('Instant B&W preview conversion failed:', err);
        if (els.previewBwStatus) els.previewBwStatus.textContent = 'Ready for Loomis Analysis';
      } finally {
        if (els.previewBwSpinner) els.previewBwSpinner.classList.add('hidden');
      }
    };
    reader.readAsDataURL(file);
  }

  // ── EXPORTING ─────────────────────────────────────────────────────────
  function downloadCurrentStage() {
    const a = document.createElement('a');
    if (state.currentStage === 0) {
      a.href = state.bwPhotoUrl || '/input/reference_bw.jpg';
      a.download = 'loomis_bw_reference.jpg';
    } else {
      const pad = String(state.currentStage).padStart(2, '0');
      a.href = `/output/hand_drawn/stage_${pad}.png`;
      a.download = `loomis_stage_${pad}.png`;
    }
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }

  // ── EVENT LISTENERS SETUP ─────────────────────────────────────────────
  function setupEventListeners() {
    // Mode tabs
    els.modeTabs.forEach(tab => {
      tab.addEventListener('click', () => setViewMode(tab.dataset.mode));
    });

    // Scrubber slider
    els.stageSlider.addEventListener('input', e => {
      pausePlayback();
      setStage(parseInt(e.target.value, 10));
    });

    // Playback buttons
    els.btnPrevStage.addEventListener('click', () => {
      pausePlayback();
      setStage(state.currentStage - 1);
    });

    els.btnNextStage.addEventListener('click', () => {
      pausePlayback();
      setStage(state.currentStage + 1);
    });

    els.btnPlayPause.addEventListener('click', togglePlayPause);

    els.selSpeed.addEventListener('change', e => {
      state.playSpeed = parseInt(e.target.value, 10);
      if (state.isPlaying) {
        clearInterval(state.playInterval);
        state.playInterval = setInterval(() => {
          if (state.currentStage < 20) {
            setStage(state.currentStage + 1);
          } else {
            pausePlayback();
          }
        }, state.playSpeed);
      }
    });

    // Split curtain slider dragging
    els.splitContainer.addEventListener('mousedown', e => {
      isDraggingSplit = true;
      handleSplitDrag(e);
    });
    window.addEventListener('mousemove', handleSplitDrag);
    window.addEventListener('mouseup', () => { isDraggingSplit = false; });

    els.splitContainer.addEventListener('touchstart', e => {
      isDraggingSplit = true;
      handleSplitDrag(e);
    });
    window.addEventListener('touchmove', handleSplitDrag);
    window.addEventListener('touchend', () => { isDraggingSplit = false; });

    // Onion slider
    els.onionSlider.addEventListener('input', e => {
      const val = e.target.value;
      els.onionDrawingImg.style.opacity = val / 100;
      els.onionValue.textContent = `${val}%`;
    });

    // Reference Mode Toggles
    if (els.btnRefBW) {
      els.btnRefBW.addEventListener('click', () => setReferenceMode('bw'));
    }
    if (els.btnRefColor) {
      els.btnRefColor.addEventListener('click', () => setReferenceMode('color'));
    }

    // Header actions
    els.btnOpenUpload.addEventListener('click', openUploadModal);
    els.btnDownloadCurrent.addEventListener('click', downloadCurrentStage);
    if (els.btnDownloadZip) {
      els.btnDownloadZip.addEventListener('click', downloadZipPackage);
    }

    // Modal
    els.btnCloseUpload.addEventListener('click', closeUploadModal);
    els.btnCancelUpload.addEventListener('click', closeUploadModal);
    els.btnBrowse.addEventListener('click', e => {
      e.stopPropagation();
      els.fileInput.click();
    });
    els.dropzone.addEventListener('click', () => els.fileInput.click());
    els.fileInput.addEventListener('change', e => {
      if (e.target.files && e.target.files[0]) {
        handleFileSelected(e.target.files[0]);
      }
    });

    // Drag and drop
    els.dropzone.addEventListener('dragover', e => {
      e.preventDefault();
      els.dropzone.classList.add('dragover');
    });
    els.dropzone.addEventListener('dragleave', () => {
      els.dropzone.classList.remove('dragover');
    });
    els.dropzone.addEventListener('drop', e => {
      e.preventDefault();
      els.dropzone.classList.remove('dragover');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileSelected(e.dataTransfer.files[0]);
      }
    });

    els.btnRemoveFile.addEventListener('click', e => {
      e.stopPropagation();
      resetDropzone();
    });

    els.btnStartProcessing.addEventListener('click', processUploadedImage);

    // Keyboard shortcuts
    window.addEventListener('keydown', e => {
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
      if (e.code === 'Space') {
        e.preventDefault();
        togglePlayPause();
      } else if (e.code === 'ArrowLeft') {
        e.preventDefault();
        pausePlayback();
        setStage(state.currentStage - 1);
      } else if (e.code === 'ArrowRight') {
        e.preventDefault();
        pausePlayback();
        setStage(state.currentStage + 1);
      }
    });

    // Quick tools
    els.chkPaperTooth.addEventListener('change', e => {
      const frames = document.querySelectorAll('.paper-frame');
      frames.forEach(f => {
        f.classList.toggle('no-tooth', !e.target.checked);
      });
    });

    els.btnFullscreen.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        els.canvasViewport.requestFullscreen().catch(err => alert(err.message));
      } else {
        document.exitFullscreen();
      }
    });

    // AI Art Coach prompt listeners
    if (els.btnCoachProportions) {
      els.btnCoachProportions.addEventListener('click', () => {
        const tip = COACH_TIPS[state.currentStage];
        const yawText = els.tYaw.textContent || '0°';
        const pitchText = els.tPitch.textContent || '0°';
        els.coachSpeechBubble.textContent = `📐 [Head Proportions for Stage ${state.currentStage}]: Current subject head orientation is Yaw ${yawText}, Pitch ${pitchText}. ${tip ? tip.proportions : ''}`;
      });
    }

    if (els.btnCoachTechnique) {
      els.btnCoachTechnique.addEventListener('click', () => {
        const tip = COACH_TIPS[state.currentStage];
        els.coachSpeechBubble.textContent = `✏️ [Sketch Technique for Stage ${state.currentStage}]: ${tip ? tip.technique : ''}`;
      });
    }

    if (els.btnCoachMistakes) {
      els.btnCoachMistakes.addEventListener('click', () => {
        const tip = COACH_TIPS[state.currentStage];
        els.coachSpeechBubble.textContent = `⚠️ [Common Pitfalls in Stage ${state.currentStage}]: ${tip ? tip.mistakes : ''}`;
      });
    }

    if (els.btnCoachPencil) {
      els.btnCoachPencil.addEventListener('click', () => {
        const tip = COACH_TIPS[state.currentStage];
        els.coachSpeechBubble.textContent = `🎨 [Graphite & Pressure Guidance]: ${tip ? tip.pencils : ''}`;
      });
    }

    // Direct Canvas Drag & Drop
    ['dragenter', 'dragover'].forEach(eventName => {
      els.canvasViewport.addEventListener(eventName, e => {
        e.preventDefault();
        e.stopPropagation();
        els.canvasViewport.style.outline = '2px dashed var(--gold-primary)';
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      els.canvasViewport.addEventListener(eventName, e => {
        e.preventDefault();
        e.stopPropagation();
        els.canvasViewport.style.outline = 'none';
      });
    });

    els.canvasViewport.addEventListener('drop', e => {
      const dt = e.dataTransfer;
      if (dt && dt.files && dt.files[0]) {
        handleFileSelected(dt.files[0]);
        processUploadedImage();
      }
    });

    // Checkpoint completion button
    if (els.btnVerifyCheckpoint) {
      els.btnVerifyCheckpoint.addEventListener('click', handleVerifyCheckpoint);
    }
  }

  // Run on DOM load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
