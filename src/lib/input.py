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

CONTROLS_CONFIRM = "confirm"
CONTROLS_CANCEL = "cancel"
CONTROLS_MANAGE = "manage"
CONTROLS_RUN = "run"
CONTROLS_TURN = "turn"
CONTROLS_ITEM = "item"
CONTROLS_WAIT = "wait"
CONTROLS_SHORTCUT = "shortcut"
CONTROLS_ALLY = "ally"
CONTROLS_SKILL = "skill"
CONTROLS_INVENTORY = "inventory"
CONTROLS_PAUSE = "pause"
CONTROLS_MINIMAP = "minimap"

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
  if type(control) is list:
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
