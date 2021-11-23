_buttons = {}
_controls = {}
timings = {}

BUTTON_LEFT = "left"
BUTTON_RIGHT = "right"
BUTTON_UP = "up"
BUTTON_DOWN = "down"
BUTTON_A = "a"
BUTTON_B = "b"
BUTTON_X = "x"
BUTTON_Y = "y"
BUTTON_L = "l"
BUTTON_R = "r"
BUTTON_START = "start"
BUTTON_SELECT = "select"

CONTROL_CONFIRM = "confirm"
CONTROL_CANCEL = "cancel"
CONTROL_MANAGE = "manage"
CONTROL_RUN = "run"
CONTROL_TURN = "turn"
CONTROL_ITEM = "item"
CONTROL_WAIT = "wait"
CONTROL_SHORTCUT = "shortcut"
CONTROL_ALLY = "ally"
CONTROL_SKILL = "skill"
CONTROL_INVENTORY = "inventory"
CONTROL_PAUSE = "pause"
CONTROL_MINIMAP = "minimap"

ARROW_DELTAS = {
  BUTTON_LEFT: (-1, 0),
  BUTTON_RIGHT: (1, 0),
  BUTTON_UP: (0, -1),
  BUTTON_DOWN: (0, 1),
}

def config(buttons=None, controls=None):
  global _buttons, _controls
  _buttons = buttons or _buttons
  _controls = controls or _controls

def resolve_button(button):
  return next((k for k, bs in _buttons.items() if button in bs), None)

def resolve_delta(button):
  button = resolve_button(button)
  return ARROW_DELTAS[button] if button in ARROW_DELTAS else None

def handle_press(button):
  button = resolve_button(button)
  if button is not None and button not in timings:
    timings[button] = 1

def handle_release(button):
  button = resolve_button(button)
  if button is not None:
    del timings[button]

def get_state(control):
  if control in _controls:
    button = None
    for button in _controls[control]:
      if not get_state(button):
        return 0
    else:
      if button:
        return get_state(button)
      else:
        return 0
  else:
    return timings[control] if control in timings else 0

def update():
  for button in timings:
    timings[button] += 1
