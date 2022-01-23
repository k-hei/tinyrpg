from math import inf

_buttons = {}
_controls = {}
timings = {}
latest = None

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

def resolve_control(button):
  button = resolve_button(button) or button
  controls = [c for c, bs in _controls.items() if button in bs]
  for control in controls:
    if get_state(control):
      return control

def resolve_controls(button):
  button = resolve_button(button) or button
  controls = [c for c, bs in _controls.items() if next((b for b in bs if b == button or isinstance(b, (tuple, list)) and button in b), False)]
  matches = [c for c in controls if get_state(c)]
  return matches

def resolve_delta(button=None, fixed_axis=False):
  if button is None:
    return resolve_delta_held(fixed_axis)
  button = resolve_button(button) or button
  return ARROW_DELTAS[button] if button in ARROW_DELTAS else (0, 0)

def backresolve_delta(delta):
  return next((b for b, d in ARROW_DELTAS.items() if d == delta), None)

def resolve_delta_held(fixed_axis=False):
    delta_x = 0
    delta_y = 0
    time_x = inf
    time_y = inf

    if (get_state(BUTTON_LEFT)
    and (not get_state(BUTTON_RIGHT)
      or get_state(BUTTON_LEFT) < get_state(BUTTON_RIGHT)
    )):
      delta_x = -1
      time_x = get_state(BUTTON_LEFT)
    elif (get_state(BUTTON_RIGHT)
    and (not get_state(BUTTON_LEFT)
      or get_state(BUTTON_RIGHT) < get_state(BUTTON_LEFT)
    )):
      delta_x = 1
      time_x = get_state(BUTTON_RIGHT)

    if (get_state(BUTTON_UP)
    and (not get_state(BUTTON_DOWN)
      or get_state(BUTTON_UP) < get_state(BUTTON_DOWN)
    )):
      delta_y = -1
      time_y = get_state(BUTTON_UP)
    elif (get_state(BUTTON_DOWN)
    and (not get_state(BUTTON_UP)
      or get_state(BUTTON_DOWN) < get_state(BUTTON_UP)
    )):
      delta_y = 1
      time_y = get_state(BUTTON_DOWN)

    if fixed_axis and time_x < time_y:
      return (delta_x, 0)
    elif fixed_axis and time_y <= time_x:
      return (0, delta_y)

    return (delta_x, delta_y)

def is_delta_button(button):
  return resolve_button(button) in ARROW_DELTAS

def is_control_pressed(control):
  if control not in _controls:
    return False
  return next((True for b in _controls[control] if get_state(b)), False)

def handle_press(button):
  global latest
  latest = button

  if button not in timings:
    timings[button] = 1

  button = resolve_button(button)
  if button not in timings and button is not None:
    timings[button] = 1

def handle_release(button):
  if button in timings:
    del timings[button]

  button = resolve_button(button)
  if button in timings and button is not None:
    del timings[button]

def get_state(control):
  if control in _controls:
    button = None
    for button in _controls[control]:
      state = get_state(button)
      if state:
        return state
    else:
      return 0

  if isinstance(control, (tuple, list)):
    for button in control:
      if not get_state(button):
        return 0
    else:
      if button:
        return get_state(button)
      else:
        return 0

  if control in timings:
    return timings[control]

  control = resolve_button(control)
  if control in timings:
    return timings[control]

  return 0

def get_latest_button():
  return latest

def update():
  for button in timings:
    timings[button] += 1
