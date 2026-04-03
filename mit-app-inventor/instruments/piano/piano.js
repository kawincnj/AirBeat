/**
 * MIRRORS python_logic_instruments/Piano/test_piano01.py
 * Specific logic for the Piano instrument.
 */
class PianoInstrument {
  constructor(soundManager) {
    this.soundManager = soundManager;
    this.keys = ["C4","D4","E4","F4","G4","A4","B4","C5","D5","E5","F5","G5","A5"];
    this.keyboardHeightRatio = 0.25; // Ratio of screen height
    this.previousPressedIndices = new Set();
    this.currentPressedIndices = new Set();
    
    // Finger tip landmark IDs in MediaPipe
    this.FINGER_TIPS = [4, 8, 12, 16, 20];
    
    // Mirroring state
    this.isMirrored = true;
  }

  async setup() {
    console.log("Setting up Piano sounds...");
    const promises = this.keys.map(note => 
      this.soundManager.loadSound(note, `sounds/${note.toLowerCase()}.ogg`)
    );
    await Promise.all(promises);
  }

  setMirror(value) {
    this.isMirrored = value;
  }

  drawInstrument(ctx, canvasWidth, canvasHeight) {
    const keyWidth = canvasWidth / this.keys.length;
    const yStart = canvasHeight * (1 - this.keyboardHeightRatio);

    ctx.save();
    
    for (let i = 0; i < this.keys.length; i++) {
      // FIX: If mirrored, we need to draw in reverse order so that 
      // index 0 (C4) stays on the visual LEFT.
      let x1;
      if (this.isMirrored) {
          // In a mirrored context, context-x=0 is visual-right.
          // To get visual-left (index 0), we draw at context-x = width - keyWidth.
          x1 = canvasWidth - (i + 1) * keyWidth;
      } else {
          x1 = i * keyWidth;
      }

      const note = this.keys[i];

      ctx.globalAlpha = 0.6;
      if (this.currentPressedIndices.has(i)) {
        ctx.fillStyle = "#00ff00";
      } else {
        ctx.fillStyle = "#ffffff";
      }

      ctx.fillRect(x1, yStart, keyWidth, canvasHeight - yStart);
      
      ctx.strokeStyle = "#000000";
      ctx.lineWidth = 2;
      ctx.strokeRect(x1, yStart, keyWidth, canvasHeight - yStart);

      // Draw text (Correctly un-mirrored for readability)
      ctx.save();
      ctx.globalAlpha = 1.0;
      ctx.fillStyle = "#000000";
      ctx.font = `bold ${keyWidth * 0.35}px Arial`;
      ctx.textAlign = "center";
      
      const textX = x1 + keyWidth / 2;
      const textY = canvasHeight - 20;

      if (this.isMirrored) {
          ctx.translate(textX, textY);
          ctx.scale(-1, 1); // Flip text back to normal
          ctx.fillText(note, 0, 0);
      } else {
          ctx.fillText(note, textX, textY);
      }
      ctx.restore();
    }
    ctx.restore();
  }

  processHand(landmarks, handedness) {
    const yStartRatio = 1 - this.keyboardHeightRatio;
    
    for (const tipId of this.FINGER_TIPS) {
      const tip = landmarks[tipId];
      
      if (tip.y > yStartRatio) {
        let logicalX = tip.x;
        // Map MediaPipe X to our key indices
        // If mirrored, raw x=1.0 is the visual left (Key 0)
        if (this.isMirrored) {
            logicalX = 1.0 - tip.x;
        }

        const keyIndex = Math.floor(logicalX * this.keys.length);
        if (keyIndex >= 0 && keyIndex < this.keys.length) {
          this.currentPressedIndices.add(keyIndex);
        }
      }
    }
    
    return this.currentPressedIndices.size > 0 ? "PLAYING" : "NONE";
  }

  updateSounds() {
    for (const idx of this.currentPressedIndices) {
      if (!this.previousPressedIndices.has(idx)) {
        this.soundManager.play(this.keys[idx]);
      }
    }
    this.previousPressedIndices = new Set(this.currentPressedIndices);
    this.currentPressedIndices.clear();
  }
}
window.PianoInstrument = PianoInstrument;
