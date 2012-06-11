def clamp(value, low, high):
    assert low <= high
    
    return min(value, max(value, high))
