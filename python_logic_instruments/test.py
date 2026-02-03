import pygame
import time

pygame.mixer.init()

cajon_off = pygame.mixer.Sound('python_logic_instruments/sounds/cajon-off.wav')
cajon_on = pygame.mixer.Sound('python_logic_instruments/sounds/cajon-on.wav')

# Play together
for i in range(10):
    cajon_off.play()
    time.sleep(0.6)
    cajon_on.play()
    time.sleep(0.45)
    cajon_off.play()
    time.sleep(0.3)
    cajon_off.play()
    time.sleep(0.16)
    cajon_off.play()
    time.sleep(0.3)
    cajon_on.play()
    time.sleep(0.7)
