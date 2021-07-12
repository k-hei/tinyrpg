from pygame import Surface, PixelArray, Color, SRCALPHA
from colors import darken_color, rgbify, hexify

COLOR_KEY = (255, 0, 255)

def darken_image(surface):
  width, height = surface.get_size()
  new_surface = Surface(surface.get_size(), SRCALPHA)
  new_surface.blit(surface, (0, 0))
  pixels = PixelArray(new_surface)
  for y in range(height):
    for x in range(width):
      if pixels[x, y] in (0, COLOR_KEY): continue
      pixels[x, y] = Color(*darken_color(pixels[x, y]))
  return new_surface

def recolor(surface, color):
  width, height = surface.get_size()
  new_surface = Surface(surface.get_size(), SRCALPHA)
  new_surface.blit(surface, (0, 0))
  pixels = PixelArray(new_surface)
  for y in range(height):
    for x in range(width):
      if pixels[x, y] in (0, COLOR_KEY): continue
      pixels[x, y] = color
  pixels.close()
  return new_surface

def replace_color(surface, old_color, new_color):
  new_surface = Surface(surface.get_size())
  new_surface.fill(COLOR_KEY)
  new_surface.blit(surface, (0, 0))
  pixels = PixelArray(new_surface)
  pixels.replace(Color(*old_color), Color(*new_color))
  pixels.close()
  new_surface.set_colorkey(COLOR_KEY)
  return new_surface

def outline(surface, color):
  width, height = surface.get_size()
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

def stroke(surface, color):
  width, height = surface.get_size()
  new_surface = Surface((width + 2, height + 2), SRCALPHA)
  recolored_surface = recolor(surface, color)
  new_surface.blit(recolored_surface, (0, 1))
  new_surface.blit(recolored_surface, (1, 0))
  new_surface.blit(recolored_surface, (2, 1))
  new_surface.blit(recolored_surface, (1, 2))
  new_surface.blit(surface, (1, 1))
  return new_surface

def shadow(surface, color):
  width, height = surface.get_size()
  new_surface = Surface((width + 1, height + 1), SRCALPHA)
  recolored_surface = recolor(surface, color)
  new_surface.blit(recolored_surface, (1, 0))
  new_surface.blit(recolored_surface, (1, 1))
  new_surface.blit(recolored_surface, (0, 1))
  new_surface.blit(surface, (0, 0))
  return new_surface

def shadow_lite(surface, color):
  width, height = surface.get_size()
  new_surface = Surface((width + 1, height + 1), SRCALPHA)
  recolored_surface = recolor(surface, color)
  new_surface.blit(recolored_surface, (1, 1))
  new_surface.blit(surface, (0, 0))
  return new_surface
