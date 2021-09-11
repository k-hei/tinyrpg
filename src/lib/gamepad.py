import pygame

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
L1 = "l1"
R1 = "r1"
L = "l1"
R = "r1"
TRIANGLE = "triangle"
CIRCLE = "circle"
CROSS = "cross"
X = "cross"
SQUARE = "square"
MENU = "menu"
PS = "menu"
mappings = [SELECT, L3, R3, START, UP, RIGHT, DOWN, LEFT, L2, R2, L1, R1, TRIANGLE, CIRCLE, CROSS, SQUARE, MENU]

def init():
  pygame.joystick.init()

def config(preset=None):
  global controls
  controls = preset

def handle_event(app, event):
  global inited
  if not inited:
    inited = True
    gamepad = pygame.joystick.Joystick(0)
    gamepad.init()
  if event.type == pygame.JOYBUTTONDOWN:
    handle_press(app, mappings[event.button])
    return True
  if event.type == pygame.JOYBUTTONUP:
    handle_release(app, mappings[event.button])
    return True
  return False

def handle_press(app, button):
  timings[button] = 1
  print(button)
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

def update():
  for button in timings:
    timings[button] += 1
