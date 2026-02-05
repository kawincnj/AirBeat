import numpy as np

def find_len_after_deci(double):
    """Optimized decimal length finder"""
    str_parts = str(double).split('.')
    if len(str_parts) < 2:
        return 0
    decimal_part = str_parts[1]
    for i, char in enumerate(decimal_part, 1):
        if char != '0':
            return i
    return len(decimal_part)

def hand_up(hand_up, z, is_upper,threshold_upper=0.02, threshold_lower = 0.02):
    """Determine if hand is up based on z-coordinate threshold"""
    # Simplified logic for speed
    return abs(z) >= threshold_upper if is_upper else abs(z) >= threshold_lower