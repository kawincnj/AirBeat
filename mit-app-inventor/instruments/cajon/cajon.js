/**
 * MIRRORS python_logic_instruments/Cajon/cajonV2.py
 * Specific logic for the Cajon instrument.
 */
class CajonInstrument {
  constructor(soundManager, poseClassifier) {
      this.soundManager = soundManager;
      this.poseClassifier = poseClassifier;
      this.ySeparate = 0.5; // Normalized center line
      this.isDragging = false;

      // Track previous states per hand
      this.leftPrevUp = true;
      this.rightPrevUp = true;
  }

  async setup() {
      console.log("Setting up Cajon sounds...");
      await this.soundManager.loadSound('cajon_on', 'sounds/cajon-on.wav');
      await this.soundManager.loadSound('cajon_off', 'sounds/cajon-off.wav');
  }

  setYSeparate(y) {
      // Clamp between 0.1 and 0.9 to keep it on screen
      this.ySeparate = Math.max(0.1, Math.min(0.9, y));
  }

  drawInstrument(ctx, canvasWidth, canvasHeight) {
      const yPos = canvasHeight * this.ySeparate;

      // Draw the center line
      ctx.strokeStyle = this.isDragging ? '#ffaa00' : '#4488ff';
      ctx.lineWidth = this.isDragging ? 5 : 3;
      ctx.setLineDash(this.isDragging ? [] : [20, 10]);

      ctx.beginPath();
      ctx.moveTo(0, yPos);
      ctx.lineTo(canvasWidth, yPos);
      ctx.stroke();
      ctx.setLineDash([]);

      // Draw a small "handle" indicator on the right
      ctx.fillStyle = this.isDragging ? '#ffaa00' : '#4488ff';
      ctx.beginPath();
      ctx.arc(canvasWidth - 30, yPos, 10, 0, Math.PI * 2);
      ctx.fill();

      // Instructions when dragging
      if (this.isDragging) {
          ctx.fillStyle = '#ffaa00';
          ctx.font = 'bold 20px sans-serif';
          ctx.textAlign = 'right';
          ctx.fillText('Adjusting Line...', canvasWidth - 50, yPos - 15);
      }
  }


  processHand(landmarks, handedness) {
    const pose = this.poseClassifier.classify(landmarks);
    const isUp = pose === "up";
    const status = isUp ? "UP" : pose === "down" ? "DOWN" : "NONE";
    const wristY = landmarks[1].y;

    if (handedness === "Right") {
      // Trigger logic: UP -> NOT UP transition
      if (this.rightPrevUp && !isUp) {
        this.triggerHit(wristY);
      }
      this.rightPrevUp = isUp;
    } else {
      if (this.leftPrevUp && !isUp) {
        this.triggerHit(wristY);
      }
      this.leftPrevUp = isUp;
    }
    return status;
  }

  triggerHit(wristY) {
    if (wristY < this.ySeparate) {
      this.soundManager.play("cajon_on");
    } else {
      this.soundManager.play("cajon_off");
    }
  }
}
window.CajonInstrument = CajonInstrument;
