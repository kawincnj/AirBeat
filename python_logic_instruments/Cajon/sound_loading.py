import pygame
from threading import Thread

# Optimized pygame mixer settings for minimal latency
pygame.mixer.pre_init(
    frequency=22050,  # Lower frequency = less latency (was 44100)
    size=-16,
    channels=2,
    buffer=256  # Smaller buffer = less latency (was 512)
)
pygame.mixer.init()

# Pre-load sounds
cajon_off = pygame.mixer.Sound('python_logic_instruments/sounds/cajon-off.wav')
cajon_on = pygame.mixer.Sound('python_logic_instruments/sounds/cajon-on.wav')

# Pre-allocate channels for immediate playback
pygame.mixer.set_num_channels(8)  # Multiple channels allow overlapping sounds
channel_off = pygame.mixer.Channel(0)
channel_on = pygame.mixer.Channel(1)

# Set volume for faster response (optional)
cajon_off.set_volume(1.0)
cajon_on.set_volume(1.0)

def play_cajon_off():
    """Play cajon off sound with minimum latency"""
    channel_off.play(cajon_off)

def play_cajon_on():
    """Play cajon on sound with minimum latency"""
    channel_on.play(cajon_on)

# Alternative async versions (uncomment if you want to test threading approach)
# def play_cajon_off_async():
#     """Play sound in separate thread to avoid blocking main loop"""
#     Thread(target=lambda: channel_off.play(cajon_off), daemon=True).start()
# 
# def play_cajon_on_async():
#     """Play sound in separate thread to avoid blocking main loop"""
#     Thread(target=lambda: channel_on.play(cajon_on), daemon=True).start()
