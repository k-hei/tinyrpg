def ease_in(t):
  return t * t

def ease_out(t):
  return -t * (t - 2)

def ease_in_out(t):
  return ease_in(t * 2) / 2 if t < 0.5 else (ease_out(t * 2 - 1) + 1) / 2
