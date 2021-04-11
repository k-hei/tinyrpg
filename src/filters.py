from pygame import Surface, PixelArray

COLOR_KEY = (255, 0, 255)

def recolor(surface, color):
  (width, height) = surface.get_size()
  new_surface = Surface((width, height))
  new_surface.fill(COLOR_KEY)
  new_surface.blit(surface, (0, 0))
  pixels = PixelArray(new_surface)
  colorkey = new_surface.map_rgb(COLOR_KEY)
  colorkey_scaled = 4294902015
  for y in range(height):
    for x in range(width):
      if pixels[x, y] != colorkey and pixels[x, y] != colorkey_scaled:
        pixels[x, y] = color
  new_surface.set_colorkey(COLOR_KEY)
  return new_surface

def outline(surface, color):
  (width, height) = surface.get_size()
  new_surface = Surface((width + 2, height + 2))
  new_surface.fill(COLOR_KEY)
  new_surface.set_colorkey(COLOR_KEY)
  recolored_surface = recolor(surface, color)
  for y in range(3):
    for x in range(3):
      if x == 1 and y == 1:
        continue
      new_surface.blit(recolored_surface, (x, y))
  new_surface.blit(surface, (1, 1))
  return new_surface

def shadow(surface, color):
  (width, height) = surface.get_size()
  new_surface = Surface((width + 1, height + 1))
  new_surface.fill(COLOR_KEY)
  new_surface.set_colorkey(COLOR_KEY)
  recolored_surface = recolor(surface, color)
  new_surface.blit(recolored_surface, (1, 0))
  new_surface.blit(recolored_surface, (1, 1))
  new_surface.blit(recolored_surface, (0, 1))
  new_surface.blit(surface, (0, 0))
  return new_surface
