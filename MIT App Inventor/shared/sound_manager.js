/**
 * MIRRORS plugin/sound_manager.py
 * Handles loading and playing sounds using Web Audio API for low latency.
 */
class SoundManager {
    constructor() {
        this.audioCtx = null;
        this.sounds = {};
    }

    async init() {
        if (!this.audioCtx) {
            this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }
        if (this.audioCtx.state === 'suspended') {
            await this.audioCtx.resume();
        }
    }

    async loadSound(name, url) {
        if (!this.audioCtx) await this.init();
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const arrayBuffer = await response.arrayBuffer();
            const audioBuffer = await this.audioCtx.decodeAudioData(arrayBuffer);
            this.sounds[name] = audioBuffer;
            console.log(`Sound loaded: ${name}`);
            return true;
        } catch (e) {
            console.error(`Failed to load sound ${name} from ${url}:`, e);
            return false;
        }
    }

    play(name) {
        if (!this.sounds[name] || !this.audioCtx) return;
        const source = this.audioCtx.createBufferSource();
        source.buffer = this.sounds[name];
        source.connect(this.audioCtx.destination);
        source.start(0);
    }
}
window.SoundManager = SoundManager;
