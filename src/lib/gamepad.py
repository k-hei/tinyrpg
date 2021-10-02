import pygame
import debug

inited = False
timings = {}
controls = None

SELECT = "select"
L3 = "l3"
R3 = "r3"
START = "start"
UP = "up"
RIGHT = "right"
DOWN = "down"
LEFT = "left"
L2 = "l2"
R2 = "r2"
L1 = "l"
R1 = "r"
L = "l"
R = "r"
TRIANGLE = "y"
CIRCLE = "a"
CROSS = "b"
X = "b"
SQUARE = "x"
MENU = "menu"
PS = "menu"
OPTIONS = "options"
TOUCH = "touch"
SHARE = "share"
mappings = [SELECT, L3, R3, START, UP, RIGHT, DOWN, LEFT, L2, R2, L1, R1, TRIANGLE, CIRCLE, CROSS, SQUARE, MENU, OPTIONS, TOUCH, SHARE]

def init():
  pygame.joystick.init()

def init_gamepad(device_index):
  if pygame.joystick.get_count():
      gamepad = pygame.joystick.Joystick(device_index)
      gamepad.init()

def config(preset=None):
  global controls
  controls = preset

def handle_event(app, event):
  global inited
  if not inited:
    inited = True
    init_gamepad(0)
  if event.type == pygame.JOYBUTTONDOWN:
    handle_press(app, get_mapping(event.button))
    return True
  if event.type == pygame.JOYBUTTONUP:
    handle_release(app, get_mapping(event.button))
    return True
  if event.type == pygame.JOYDEVICEADDED:
    pygame.joystick.init() # TODO: figure out why hotplugging is broken (related to duplicate code in app init)
    init_gamepad(0)
    return True
  return False

def handle_press(app, button):
  timings[button] = 1
  if app.child:
    app.child.handle_press(button)

def handle_release(app, button):
  del timings[button]
  if app.child:
    app.child.handle_release(button)

def get_state(binding):
  if type(binding) in (tuple, list):
    for button in binding:
      if not get_state(button):
        return 0
    else:
      return get_state(button)
  if binding in timings:
    return timings[binding]
  else:
    return 0

def get_mapping(button):
  return mappings[button] if button in mappings else str(button)

def update():
  for button in timings:
    timings[button] += 1
