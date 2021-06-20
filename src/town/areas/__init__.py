from math import sin, pi
from dataclasses import dataclass
from assets import load as use_assets
from filters import stroke, replace_color
from palette import BLACK, WHITE, GRAY, BLUE
from config import TILE_SIZE, WINDOW_WIDTH
from sprite import Sprite
from town.actors.npc import Npc

def can_talk(hero, actor):
  if (not isinstance(actor, Npc)
  or not actor.messages
  or actor.core.faction == "player"):
    return False
  dist_x = actor.x - hero.x
  facing_x, _ = hero.facing
  return abs(dist_x) < TILE_SIZE * 1.5 and dist_x * facing_x >= 0

def find_nearby_link(hero, links):
  for link in links.values():
    dist_x = link.x - hero.x
    _, direction_y = link.direction
    if abs(dist_x) < TILE_SIZE // 2 and direction_y:
      return link

ARROW_PERIOD = 45
ARROW_BOUNCE = 2

@dataclass
class AreaLink:
  x: int
  direction: tuple[int, int]

class Area:
  bg = None
  width = WINDOW_WIDTH
  ACTOR_Y = 128
  HORIZON_NORTH = -40
  TRANSIT_NORTH = -20
  HORIZON_SOUTH = 60
  TRANSIT_SOUTH = 30

  def __init__(area):
    area.actors = []
    area.camera = None
    area.draws = 0

  def init(area, ctx):
    pass

  def spawn(area, actor, pos):
    area.actors.append(actor)
    actor.pos = pos

  def view(area, sprites, hero):
    assets = use_assets().sprites
    bg_image = assets[area.bg]
    area.width = bg_image.get_width()
    hero_x, _ = hero.pos
    bg_x = max(0, min(area.width - WINDOW_WIDTH, hero_x - WINDOW_WIDTH / 2))
    sprites.append(Sprite(
      image=bg_image,
      pos=(-bg_x, 0)
    ))
    for actor in sorted(area.actors, key=lambda actor: 1 if actor is hero else 0):
      for sprite in actor.view():
        y = 128 if actor.get_faction() == "player" else 120
        sprite.move((-bg_x, y))
        sprites.append(sprite)
