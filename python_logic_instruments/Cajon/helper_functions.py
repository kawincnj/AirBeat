import numpy as np

def hand_up(hand_up, z, is_upper,threshold_upper=0.02, threshold_lower = 0.02):
    """Determine if hand is up based on z-coordinate threshold"""
    # Simplified logic for speed
    return abs(z) >= threshold_upper if is_upper else abs(z) >= threshold_lower