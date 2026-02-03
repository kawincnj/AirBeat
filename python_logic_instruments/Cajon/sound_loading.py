import pygame

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
# Using a small buffer (512) reduces the delay between the trigger and the sound

cajon_off = pygame.mixer.Sound('python_logic_instruments/sounds/cajon-off.wav')
cajon_on = pygame.mixer.Sound('python_logic_instruments/sounds/cajon-on.wav')

def play_cajon_off():
    cajon_off.play() # No sleep here!

def play_cajon_on():
    cajon_on.play() # No sleep here!