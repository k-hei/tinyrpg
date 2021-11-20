_controls = {}

def config(controls):
  global _controls
  _controls = controls

def resolve_button(button):
  return _controls[button] if button in _controls else None

def resolve_delta(button):
  button = resolve_button(button)
  return None
