import math
from pygame import Surface, PixelArray

# a node is a diamond. has form (x, y, t) where t is the size based on renders
# stack holds the newest nodes
# speed is how many updates are performed per frame
# update and render have to be separate in order for speed to work properly
# however, update requires knowledge of the screen size (we can predefine this in the constructor)

DIAMOND_RADIUS = 32
MULTIPLY_DELAY = 3
SPREAD_SPEED = 2

def gen_diamonds(radius, step):
  diamonds = []
  for i in range(0, radius + 1, step):
    diameter = i * 2 + 1
    start = (i, i)
    cells = [start]
    visited = [start]
    queue = [(i, i, 0)]
    while len(queue):
      x, y, steps = queue.pop()
      if steps + 1 > i:
        continue
      neighbors = [
        (x - 1, y),
        (x + 1, y),
        (x, y - 1),
        (x, y + 1)
      ]
      for neighbor in neighbors:
        if neighbor in visited:
          continue
        neighbor_x, neighbor_y = neighbor
        visited.append(neighbor)
        cells.append(neighbor)
        queue.insert(0, (neighbor_x, neighbor_y, steps + 1))
    surface = Surface((diameter, diameter))
    surface.set_colorkey((255, 0, 255))
    surface.fill((255, 0, 255))
    pixels = PixelArray(surface)
    for x, y in cells:
      pixels[x, y] = (0, 0, 0)
    pixels.close()
    diamonds.append(surface)
  return diamonds

diamonds = gen_diamonds(DIAMOND_RADIUS, SPREAD_SPEED)

class DissolveIn:
  def __init__(transit, surface):
    start = (DIAMOND_RADIUS // 2, DIAMOND_RADIUS // 2, 0)
    transit.surface = surface
    transit.stack = [start]
    transit.nodes = [start]
    transit.nodes_done = []
    transit.time = 0
    transit.done = False

  def update(transit):
    if transit.done:
      return
    view_width = transit.surface.get_width()
    view_height = transit.surface.get_height()
    old_stack = transit.stack
    new_stack = []
    if transit.time % MULTIPLY_DELAY == 0:
      while len(old_stack):
        x, y, t = old_stack.pop()
        if x < view_width and y < view_height:
          right_node = (x + DIAMOND_RADIUS, y, 0)
          bottom_node = (x, y + DIAMOND_RADIUS, 0)
          if right_node not in new_stack:
            new_stack.append(right_node)
          if bottom_node not in new_stack:
            new_stack.append(bottom_node)
      if len(new_stack) > 0:
        transit.nodes += new_stack
        transit.stack = new_stack
    for node in transit.nodes:
      x, y, t = node
      i = transit.nodes.index(node)
      if t + SPREAD_SPEED <= DIAMOND_RADIUS:
        t += SPREAD_SPEED
        transit.nodes[i] = (x, y, t)
      elif node not in transit.nodes_done:
        transit.nodes_done.append(node)
        if len(transit.nodes_done) == len(transit.nodes) and len(new_stack) == 0:
          transit.done = True
    transit.time += 1

  def render(transit):
    for node in transit.nodes:
      x, y, t = node
      diamond = diamonds[t // SPREAD_SPEED]
      transit.surface.blit(diamond, (x - t, y - t))

class DissolveOut:
  pass
