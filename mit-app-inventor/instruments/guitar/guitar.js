/**
 * MIRRORS python_logic_instruments/Guitar/Guitar.py
 * Specific logic for the Guitar instrument.
 */
class GuitarInstrument {
  constructor(soundManager) {
    this.soundManager = soundManager;
    // Normalized coordinates (0.0 to 1.0)
    this.neckBox = { x: 0.05, y: 0.4, w: 0.35, h: 0.4 }; 
    this.strumLineY = 0.65; 
    this.wasAbove = true;
    
    this.templates = [];
    this.currentChord = "Unknown";
    this.isMirrored = true;
    
    // Smooth visualization
    this.targetFX = -1;
    this.targetFY = -1;
    this.smoothFX = -1;
    this.smoothFY = -1;
  }

  async setup() {
    console.log("Setting up Guitar...");
    await this.loadTemplates();
    
    const chords = ["Am", "Bbm", "Bm", "C", "C#m", "Cm", "D", "Dm", "E", "Em", "F", "F#", "G", "G#", "Gm", "muted_strum"];
    const promises = chords.map(name => 
      this.soundManager.loadSound(name, `sounds/${name}.wav`)
    );
    await Promise.all(promises);
  }

  async loadTemplates() {
    const chordNames = ["Am", "Bbm", "Bm", "C", "C#m", "Cm", "D", "Dm", "E", "Em", "F", "F#", "G", "G#", "Gm"];
    
    for (const name of chordNames) {
      try {
        const response = await fetch(`../../../templates/guitar chords/${name}.json`);
        if (!response.ok) continue;
        const data = await response.json();
        const items = Array.isArray(data) ? data : [data];
        
        for (const d of items) {
          const vector = d.rep_vector || d.representative_vector;
          if (vector) {
            this.templates.push({
              name: d.name,
              vector: new Float32Array(vector.flat()), // Use TypedArray for speed
              fret: d.fret || 1,
              string: d.string || 1,
              anchorIdx: d.anchor_idx || 8
            });
          }
        }
      } catch (e) {
        console.warn(`Could not load template for ${name}:`, e);
      }
    }
    console.log(`Loaded ${this.templates.length} guitar chord templates.`);
  }

  setMirror(value) {
    this.isMirrored = value;
  }

  processHand(landmarks, handedness) {
    if (handedness === "Left") {
      this.processLeftHand(landmarks);
    } else {
      this.processRightHand(landmarks);
    }
    return this.currentChord;
  }

  processLeftHand(landmarks) {
    // 1. Find lead finger (highest tip) - usually the one indicating fret/string
    const fingerTipIndices = [8, 12, 16, 20];
    let leadLm = landmarks[8];
    let leadIdx = 8;
    
    for (const idx of fingerTipIndices) {
      if (landmarks[idx].y < leadLm.y) {
        leadLm = landmarks[idx];
        leadIdx = idx;
      }
    }

    // Convert raw camera X to visual screen X for hit-box checking
    let lx = this.isMirrored ? (1.0 - leadLm.x) : leadLm.x;
    let ly = leadLm.y;

    const b = this.neckBox;
    if (lx > b.x && lx < b.x + b.w && ly > b.y && ly < b.y + b.h) {
      // Calculate Fret and String based on visual position
      const fIdx = Math.floor((lx - b.x) / (b.w / 4)); // 4 frets
      const sIdx = Math.floor((ly - b.y) / (b.h / 6)); // 6 strings
      const fret = fIdx + 1;
      const string = Math.max(1, Math.min(6, 6 - sIdx));

      // Coordinates for visual highlight
      this.targetFX = b.x + (fIdx * (b.w / 4));
      this.targetFY = b.y + (sIdx * (b.h / 6));

      // Classify Pose using normalized 3D landmarks
      const processed = this.getGuitarVector(landmarks);
      let bestSim = -1;
      let bestName = "Unknown";

      for (const t of this.templates) {
        // Filter by fret/string/anchor to match Python logic
        if (t.fret === fret && t.string === string && t.anchorIdx === leadIdx) {
          const sim = this.cosineSimilarity(processed, t.vector);
          if (sim > bestSim) {
            bestSim = sim;
            bestName = t.name;
          }
        }
      }

      // 0.90 threshold for web version (might need slight adjustment vs Python)
      this.currentChord = bestSim > 0.90 ? bestName : `Unknown (${bestSim.toFixed(2)})`;
    } else {
      this.currentChord = "Align to Neck";
      this.targetFX = -1;
    }
  }

  processRightHand(landmarks) {
    const tipY = landmarks[8].y; // Index finger tip
    const isAbove = tipY < this.strumLineY;

    // Detect downward strum (Transition from above line to below line)
    if (this.wasAbove && !isAbove) {
        if (this.currentChord !== "Unknown" && this.currentChord !== "Align to Neck" && !this.currentChord.startsWith("Unknown")) {
          this.soundManager.play(this.currentChord);
        } else {
          this.soundManager.play("muted_strum");
        }
    }
    this.wasAbove = isAbove;
  }

  // Optimized vectorizer for guitar (Mirrors Python process_landmarks)
  getGuitarVector(landmarks) {
    // 3D landmarks
    const pts = landmarks.map(lm => [lm.x, lm.y, lm.z]);
    
    // 3D Distance for palm width (Match Python: linalg.norm(all_pts[5] - all_pts[17]))
    const palmWidth = Math.sqrt(
      Math.pow(pts[5][0] - pts[17][0], 2) + 
      Math.pow(pts[5][1] - pts[17][1], 2) +
      Math.pow(pts[5][2] - pts[17][2], 2)
    ) || 1.0;

    // Use landmarks 5 to 20 (fingers)
    const indices = Array.from({length: 16}, (_, i) => i + 5);
    const refPt = pts[5]; // Index finger base
    
    let vector = new Float32Array(48); // 16 pts * 3 coords
    let vecIdx = 0;
    
    for (const i of indices) {
      const p = pts[i];
      // Weights: Python code weights indices 5:8 (index finger) higher
      // Note: indices 5,6,7,8 are index finger in MP
      let weight = (i >= 10 && i <= 12) ? 2.5 : 1.0; // Matching your Python snippet weighting
      
      vector[vecIdx++] = ((p[0] - refPt[0]) / palmWidth) * weight;
      vector[vecIdx++] = ((p[1] - refPt[1]) / palmWidth) * weight;
      vector[vecIdx++] = ((p[2] - refPt[2]) / palmWidth) * weight;
    }

    // Normalize final vector
    const norm = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
    return norm > 0 ? vector.map(v => v / norm) : vector;
  }

  cosineSimilarity(v1, v2) {
    let dot = 0;
    for (let i = 0; i < v1.length; i++) dot += v1[i] * v2[i];
    return dot; // Assumes normalized
  }

  drawInstrument(ctx, canvasWidth, canvasHeight) {
    const b = this.neckBox;
    const bx = b.x * canvasWidth;
    const by = b.y * canvasHeight;
    const bw = b.w * canvasWidth;
    const bh = b.h * canvasHeight;

    ctx.save();
    
    // 1. Draw Fretboard
    ctx.strokeStyle = "white";
    ctx.lineWidth = 4;
    ctx.strokeRect(bx, by, bw, bh);

    // Draw Frets
    const fretW = bw / 4;
    ctx.strokeStyle = "#888";
    for (let i = 1; i < 4; i++) {
      ctx.beginPath();
      ctx.moveTo(bx + i * fretW, by);
      ctx.lineTo(bx + i * fretW, by + bh);
      ctx.stroke();
    }

    // Draw Strings and names
    const stringNames = ['E', 'A', 'D', 'G', 'B', 'e'];
    const zoneH = bh / 6;
    ctx.font = "bold 16px Arial";
    ctx.fillStyle = "white";
    for (let i = 0; i < 6; i++) {
      const y = by + (i * zoneH) + (zoneH / 2);
      ctx.strokeStyle = i > 2 ? "#aaa" : "#ccc";
      ctx.lineWidth = i > 2 ? 1 : 2;
      ctx.beginPath(); ctx.moveTo(bx, y); ctx.lineTo(bx + bw, y); ctx.stroke();
      ctx.fillText(stringNames[i], bx - 25, y + 5);
    }

    // 2. Draw Strum Line (Horizontal line on the right)
    const sy = this.strumLineY * canvasHeight;
    ctx.strokeStyle = this.wasAbove ? "#666" : "#0ff";
    ctx.lineWidth = 5;
    ctx.beginPath(); 
    ctx.moveTo(canvasWidth * 0.55, sy); 
    ctx.lineTo(canvasWidth * 0.95, sy); 
    ctx.stroke();
    ctx.fillStyle = this.wasAbove ? "#666" : "#0ff";
    ctx.fillText("STRUM HERE", canvasWidth * 0.7, sy - 10);

    // 3. Smoothing Highlight (The green box on the fretboard)
    if (this.targetFX !== -1) {
      if (this.smoothFX === -1) { this.smoothFX = this.targetFX; this.smoothFY = this.targetFY; }
      this.smoothFX += (this.targetFX - this.smoothFX) * 0.2;
      this.smoothFY += (this.targetFY - this.smoothFY) * 0.2;

      ctx.fillStyle = "rgba(0, 255, 0, 0.4)";
      ctx.fillRect(this.smoothFX * canvasWidth, this.smoothFY * canvasHeight, fretW, zoneH);
    } else {
      this.smoothFX = -1;
    }
    
    ctx.restore();
  }
}
window.GuitarInstrument = GuitarInstrument;
