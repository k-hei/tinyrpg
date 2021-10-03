from math import pi, sin
from pygame import Rect, Surface, PixelArray, Color, SRCALPHA
from colors import darken_color, rgbify, hexify
from easing.expo import ease_out

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
  new_surface = Surface(surface.get_size(), SRCALPHA)
  new_surface.blit(surface, (0, 0))
  pixels = PixelArray(new_surface)
  old_color = Color(*old_color)
  new_color = Color(*new_color)
  pixels.replace(old_color, new_color)
  pixels.close()
  return new_surface

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

def ripple(surface, start, end, waves=2, amplitude=4, period=90, time=0, pinch=True):
  new_surface = Surface(surface.get_size(), SRCALPHA).convert_alpha()
  new_surface.blit(surface.subsurface(Rect(0, 0, surface.get_width(), start)), (0, 0))
  for y in range(start, end):
    i = y - start
    p = i / (end - start)
    t = time + p * period
    t = (t % (period / waves) / period) * waves
    x = sin(t * 2 * pi) * (ease_out(p) if pinch else 1) * amplitude
    new_surface.blit(surface.subsurface(Rect(0, y, surface.get_width(), 1)), (x, y))
  return new_surface
