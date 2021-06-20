from math import sin, pi
from dataclasses import dataclass
from assets import load as use_assets
from filters import stroke, replace_color
from palette import BLACK, WHITE, GRAY, BLUE
from config import TILE_SIZE, WINDOW_WIDTH
from sprite import Sprite

@dataclass
class AreaLink:
  x: int
  direction: tuple[int, int]

class Area:
  ACTOR_Y = 128
  HORIZON_NORTH = -40
  TRANSIT_NORTH = -20
  HORIZON_SOUTH = 60
  TRANSIT_SOUTH = 30
  width = WINDOW_WIDTH
  bg = None

  def __init__(area):
    area.actors = []
    area.camera = None
    area.draws = 0

  def init(area, ctx):
    pass

  def spawn(area, actor, pos):
    area.actors.append(actor)
    actor.pos = pos

  def view(area, hero):
    sprites = []
    assets = use_assets().sprites
    bg_image = assets[area.bg]
    hero_x, _ = hero.pos
    area.width = bg_image.get_width()
    area.camera = min(0, max(-area.width + WINDOW_WIDTH, -hero_x + WINDOW_WIDTH / 2))
    sprites.append(Sprite(
      image=bg_image,
      pos=(area.camera, 0)
    ))
    for actor in sorted(area.actors, key=lambda actor: 1 if actor is hero else 0):
      for sprite in actor.view():
        y = 128 if actor.get_faction() == "player" else 120
        sprite.move((area.camera, y))
        sprite.target = actor
        sprites.append(sprite)
    return sprites
