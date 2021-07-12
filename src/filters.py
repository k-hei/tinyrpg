from pygame import Surface, PixelArray, Color, SRCALPHA
from colors import darken_color, rgbify, hexify

def darken_image(surface):
  width, height = surface.get_size()
  surface = surface.copy()
  pixels = PixelArray(surface)
  for y in range(height):
    for x in range(width):
      if pixels[x, y] == 0: continue
      pixels[x, y] = Color(*darken_color(pixels[x, y]))
  return surface

def recolor(surface, color):
  width, height = surface.get_size()
  surface = surface.copy()
  pixels = PixelArray(surface)
  for y in range(height):
    for x in range(width):
      if pixels[x, y] == 0: continue
      pixels[x, y] = color
  pixels.close()
  return surface

def replace_color(surface, old_color, new_color):
  surface = surface.convert_alpha()
  pixels = PixelArray(surface)
  pixels.replace(old_color, new_color)
  pixels.close()
  return surface

def outline(surface, color):
  width, height = surface.get_size()
  new_surface = Surface((width + 2, height + 2), SRCALPHA)
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
