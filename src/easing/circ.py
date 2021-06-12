from math import sqrt

def ease_in(t):
  return -sqrt(1 - pow(t, 2))

def ease_out(t):
  return sqrt(1 - pow(t - 1, 2))

def ease_in_out(t):
  return ease_in(t * 2) / 2 if t < 0.5 else (ease_out(t * 2 - 1) + 1) / 2
