from dataclasses import dataclass
from typing import Dict
from pygame import Surface, Rect
from palette import WHITE

@dataclass
class Font:
  surface: Surface
  name: str
  cell_width: int
  cell_height: int
  char_width: int
  char_height: int
  char_spacing: int
  word_spacing: int
  line_spacing: int
  cols: int
  rows: int
  order: str
  exceptions: Dict[str, str]

class Ttf:
  def __init__(ttf, font):
    ttf.font = font

  def size(ttf, text=""):
    return ttf.font.size(text)

  def render(ttf, text, color=WHITE):
    b = color & 255
    g = (color >> 8) & 255
    r = (color >> 16) & 255
    width, height = ttf.size(text)
    surface = Surface((width, height)).convert_alpha()
    surface.blit(ttf.font.render(text, False, (r, g, b)), (0, 0))
    return surface

def find_width(content: str, font: Font) -> int:
  text_width = 0
  for char in content:
    if char == " ":
      text_width += font.word_spacing
      continue
    if char in font.exceptions:
      text_width += font.exceptions[char]
    else:
      text_width += font.char_width
    text_width += font.char_spacing
  return text_width

def render(content: str, font: Font) -> Surface:
  width = find_width(content, font)
  height = font.cell_height
  surface = Surface((width, height)).convert_alpha()
  x = 0
  for char in content:
    if char == " ":
      x += font.word_spacing
      continue
    index = font.order.find(char)
    col = index % font.cols
    row = index // font.cols
    surface.blit(font.surface, (x, 0), Rect(
      (col * font.cell_width, row * font.cell_height),
      (font.cell_width, font.cell_height)))
    char_width = font.char_width
    if char in font.exceptions:
      char_width = font.exceptions[char]
    elif char.upper() in font.exceptions:
      char_width = font.exceptions[char.upper()]
    x += char_width + font.char_spacing
  return surface

def render_char(char: str, font: Font) -> Surface:
  index = font.order.find(char)
  col = index % font.cols
  row = index // font.cols
  return font.surface.subsurface(Rect(
    (col * font.cell_width, row * font.cell_height),
    (font.cell_width, font.cell_height)))
