_controls = {}
ARROW_DELTAS = {
  "left": (-1, 0),
  "right": (1, 0),
  "up": (0, -1),
  "down": (0, 1),
}

def config(controls):
  global _controls
  _controls = controls

def resolve_button(button):
  return _controls[button] if button in _controls else None

def resolve_delta(button):
  button = resolve_button(button)
  return ARROW_DELTAS[button] if button in ARROW_DELTAS else None
