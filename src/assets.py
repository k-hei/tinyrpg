import json
import traceback
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

def load_image(path, key, sprites):
  try:
    sprite = pygame.image.load(join(path, key) + ".png").convert_alpha()
  except FileNotFoundError:
    print(f"FileNotFoundError: Failed to find {key}.png at {path}")
    return

  try:
    metafile = open(join(path, key) + ".json", "r")
    metadata = json.loads(metafile.read())
  except FileNotFoundError:
    metafile = None
    key = key.replace("-", "_")
    sprites[key] = sprite
    return
  finally:
    metafile and metafile.close()

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

def load_pngfont(path, key):
  typeface = pygame.image.load(join(path, key) + ".png").convert_alpha()
  metadata = json.loads(open(join(path, key) + ".json", "r").read())
  return Font(typeface, **metadata)

def load_ttf(path, key, size):
  font = pygame.font.Font(join(path, key) + ".ttf", size)
  return Ttf(font)

def load():
  if assets.sprites:
    return assets

  pygame.display.init()
  pygame.font.init()
  surface = pygame.display.set_mode(WINDOW_SIZE)
  surface.fill((0, 0, 0))
  pygame.display.flip()

  for f in listdir(ASSETS_PATH):
    if isfile(join(ASSETS_PATH, f)):
      item_name, item_ext = splitext(f)
      if item_ext == ".png":
        try:
          load_image(ASSETS_PATH, item_name, sprites)
        except:
          print(f"Failed to load {item_name}: {traceback.format_exc()}")

  pngfont_path = join(ASSETS_PATH, "pngfont")
  for f in listdir(pngfont_path):
    item_name, item_ext = splitext(f)
    if item_ext == ".png":
      fonts[item_name] = load_pngfont(pngfont_path, item_name)

  ttf_path = join(ASSETS_PATH, "ttf")
  ttf["english"] = load_ttf(ttf_path, "PCPaintEnglishSmall", 8)
  ttf["english_large"] = load_ttf(ttf_path, "PCPaintEnglishMedium", 16)
  ttf["roman"] = load_ttf(ttf_path, "PCPaintRomanSmall", 8)
  ttf["roman_large"] = load_ttf(ttf_path, "PCPaintRomanMedium", 16)
  ttf["normal"] = load_ttf(ttf_path, "PCPaintNormalSmall", 8)
  ttf["special"] = load_ttf(ttf_path, "PCPaintSpecialMedium", 12)

  assets.sprites = sprites
  assets.fonts = fonts
  assets.ttf = ttf

sprites = {}
fonts = {}
ttf = {}
assets = Assets(sprites, fonts, ttf)
load()

def trace(sprite):
  return next((k for k, s in sprites.items() if s is sprite), None)
