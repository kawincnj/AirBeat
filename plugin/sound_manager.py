import pygame
import os

class SoundManager:
    """
    A high-performance, low-latency sound manager for AirBeat.
    Uses a Singleton pattern to ensure the mixer is only initialized once.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        # Optimized settings for minimal latency
        # frequency=44100 is standard; buffer=256 is very tight for speed.
        if not pygame.mixer.get_init():
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=256)
            pygame.mixer.init()
        
        # Pre-allocate 16 channels to allow overlapping sounds (e.g., piano chords)
        pygame.mixer.set_num_channels(16)
        self.sounds = {}
        self._initialized = True
        print("SoundManager: Mixer initialized with low-latency settings.")

    def load_sound(self, name, file_path):
        """Load a sound into memory and cache it."""
        if name in self.sounds:
            return True
            
        if not os.path.exists(file_path):
            print(f"SoundManager Error: File not found at {file_path}")
            return False
        
        try:
            self.sounds[name] = pygame.mixer.Sound(file_path)
            return True
        except Exception as e:
            print(f"SoundManager Error loading {name}: {e}")
            return False

    def load_directory(self, directory_path, prefix=""):
        """Load all .wav files from a directory."""
        if not os.path.isdir(directory_path):
            return
        for file in os.listdir(directory_path):
            if file.endswith(".wav"):
                name = prefix + os.path.splitext(file)[0]
                self.load_sound(name, os.path.join(directory_path, file))

    def play(self, name, volume=1.0):
        """Play a cached sound on the first available channel."""
        sound = self.sounds.get(name)
        if sound:
            # find_channel(True) finds an idle channel or steals the oldest playing one
            channel = pygame.mixer.find_channel(True)
            if channel:
                sound.set_volume(volume)
                channel.play(sound)
        else:
            print(f"SoundManager Warning: Sound '{name}' not loaded.")

# Global instance for easy access across all modules
sound_manager = SoundManager()
