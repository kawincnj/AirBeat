/**
 * MIRRORS python_logic_instruments/Cajon/cajonV2.py
 * Specific logic for the Cajon instrument.
 */
class CajonInstrument {
    constructor(soundManager, poseClassifier) {
        this.soundManager = soundManager;
        this.poseClassifier = poseClassifier;
        this.ySeparate = 0.5; // Normalized center line
        
        // Track previous states per hand
        this.leftPrevUp = true;
        this.rightPrevUp = true;
    }

    async setup() {
        console.log("Setting up Cajon sounds...");
        await this.soundManager.loadSound('cajon_on', 'sounds/cajon-on.wav');
        await this.soundManager.loadSound('cajon_off', 'sounds/cajon-off.wav');
    }

    drawInstrument(ctx, canvasWidth, canvasHeight) {
        // Draw the center line
        ctx.strokeStyle = '#4488ff';
        ctx.lineWidth = 3;
        ctx.setLineDash([20, 10]);
        ctx.beginPath();
        ctx.moveTo(0, canvasHeight * this.ySeparate);
        ctx.lineTo(canvasWidth, canvasHeight * this.ySeparate);
        ctx.stroke();
        ctx.setLineDash([]);
    }

    processHand(landmarks, handedness) {
        const pose = this.poseClassifier.classify(landmarks);
        const isUp = (pose === 'up');
        const status = isUp ? "UP" : (pose === 'down' ? "DOWN" : "NONE");
        const wristY = landmarks[1].y;

        if (handedness === 'Right') {
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
            this.soundManager.play('cajon_on');
        } else {
            this.soundManager.play('cajon_off');
        }
    }
}
window.CajonInstrument = CajonInstrument;
