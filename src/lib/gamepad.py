import pygame
import debug
import lib.input as input

controls = None
_timings = {}
_inited = False
_app = None

LEFT = "left"
RIGHT = "right"
UP = "up"
DOWN = "down"
A = "a"
B = "b"
X = "x"
Y = "y"
CIRCLE = "a"
CROSS = "b"
SQUARE = "x"
TRIANGLE = "y"
L = "l"
R = "r"
L1 = "l"
R1 = "r"
L2 = "l2"
R2 = "r2"
L3 = "l3"
R3 = "r3"
SELECT = "select"
START = "start"
MENU = "menu"
PS = "menu"
OPTIONS = "options"
SHARE = "share"
TOUCH = "touch"
DS3_MAPPINGS = [SELECT, L3, R3, START, UP, RIGHT, DOWN, LEFT, L2, R2, L1, R1, SQUARE, CIRCLE, CROSS, TRIANGLE, MENU, OPTIONS, TOUCH, SHARE]
DS4_MAPPINGS = [CROSS, CIRCLE, SQUARE, TRIANGLE, SHARE, MENU, OPTIONS, L3, R3, L1, R1, UP, DOWN, LEFT, RIGHT, TOUCH, SELECT, START, R1, R2]
mappings = DS3_MAPPINGS

def init():
  pygame.joystick.init()

def init_gamepad(device_index):
  if pygame.joystick.get_count():
    gamepad = pygame.joystick.Joystick(device_index)
    gamepad.init()
    debug.log(f"Device {device_index} initialized")

def config(preset=None):
  global controls
  controls = preset

def handle_event(app, event):
  global _app, _inited
  _app = app
  if not _inited:
    _inited = True
    init_gamepad(0)

  if event.type == pygame.JOYBUTTONDOWN:
    handle_press(get_mapping(event.button))
    return True
  if event.type == pygame.JOYBUTTONUP:
    handle_release(get_mapping(event.button))
    return True
  if event.type == pygame.JOYDEVICEADDED:
    pygame.joystick.init() # TODO: figure out why hotplugging is broken (related to duplicate code in app init)
    init_gamepad(0)
    return True
  return False

def handle_press(button):
  if button not in _timings:
    _timings[button] = 1
  input.handle_press(button)
  _app.child and _app.child.handle_press(button)

def handle_release(button):
  del _timings[button]
  _app.child and _app.child.handle_release(button)
  input.handle_release(button)

def get_state(binding):
  if type(binding) in (tuple, list):
    button = None
    for button in binding:
      if not get_state(button):
        return 0
    else:
      if button:
        return get_state(button)
      else:
        return 0
  if binding in _timings:
    return _timings[binding]
  else:
    return 0

def get_mapping(button):
  return mappings[button] if button < len(mappings) else str(button)

def update():
  for button in _timings:
    if _timings[button] > 1:
      handle_press(button)
    _timings[button] += 1
