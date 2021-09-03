import json
from os import listdir
from os.path import isfile, join, splitext
from dataclasses import dataclass
from typing import Dict
import pygame
from pygame import Surface, Rect
from text import Font, Ttf
from config import ASSETS_PATH, WINDOW_SIZE

@dataclass
class Assets:
  sprites: Dict[str, Surface] = None
  fonts: Dict[str, Font] = None
  ttf: Dict[str, Ttf] = None

def load_image(key, path, sprites):
  try:
    sprite = pygame.image.load(join(path, key) + ".png").convert_alpha()
  except FileNotFoundError:
    print("FileNotFoundError: Could not find", key + ".png", "at", path)
    return

  try:
    metadata = json.loads(open(join(path, key) + ".json", "r").read())
  except FileNotFoundError:
    key = key.replace("-", "_")
    sprites[key] = sprite
    return

  cell_width = 0
  cell_height = 0
  offset_x = 0
  offset_y = 0
  cols = 0
  rows = 0
  for key, value in metadata.items():
    if key == "cell_width":
      cell_width = value
    elif key == "cell_height":
      cell_height = value
    elif key == "offset_x":
      offset_x = value
    elif key == "offset_y":
      offset_y = value
    elif key == "order":
      cols = len(value[0])
      rows = len(value)
      for row in range(rows):
        for col in range(cols):
          key = value[row][col]
          if key == "": continue
          sprites[key] = sprite.subsurface(Rect(
            col * cell_width + offset_x,
            row * cell_height + offset_y,
            cell_width,
            cell_height
          ))
    elif type(value) is list:
      if type(value[0]) is list:
        sprites[key] = [sprite.subsurface(Rect(*r)) for r in value]
      else:
        rect = Rect(*value)
        sprites[key] = sprite.subsurface(rect)

def load_pngfont(key, path):
  typeface = pygame.image.load(join(path, key) + ".png").convert_alpha()
  metadata = json.loads(open(join(path, key) + ".json", "r").read())
  return Font(typeface, **metadata)

def load_ttf(key, size, path):
  font = pygame.font.Font(join(path, key) + ".ttf", size)
  return Ttf(font)

def load(path=None):
  if assets.sprites:
    return assets

  pygame.display.init()
  pygame.font.init()
  surface = pygame.display.set_mode(WINDOW_SIZE)
  surface.fill((0, 0, 0))
  pygame.display.flip()

  for f in listdir(path):
    if isfile(join(path, f)):
      item_name, item_ext = splitext(f)
      if item_ext == ".png":
        try:
          load_image(item_name, path, sprites)
        except:
          print("Failed to load {}".format(item_name))

  for f in listdir(join(path, "pngfont")):
    item_name, item_ext = splitext(f)
    if item_ext == ".png":
      fonts[item_name] = load_pngfont(item_name, join(path, "pngfont"))

  ttf["english"] = load_ttf("PCPaintEnglishSmall", 8, join(path, "ttf"))
  ttf["english_large"] = load_ttf("PCPaintEnglishMedium", 16, join(path, "ttf"))
  ttf["roman"] = load_ttf("PCPaintRomanSmall", 8, join(path, "ttf"))
  ttf["roman_large"] = load_ttf("PCPaintRomanMedium", 16, join(path, "ttf"))
  ttf["normal"] = load_ttf("PCPaintNormalSmall", 8, join(path, "ttf"))
  ttf["special"] = load_ttf("PCPaintSpecialMedium", 12, join(path, "ttf"))

  assets.sprites = sprites
  assets.fonts = fonts
  assets.ttf = ttf

sprites = {}
fonts = {}
ttf = {}
assets = Assets(sprites, fonts, ttf)
load(ASSETS_PATH)

def trace(sprite):
  return next((k for k, s in sprites.items() if s is sprite), None)
