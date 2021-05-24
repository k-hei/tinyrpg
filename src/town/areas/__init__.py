from math import sin, pi
from assets import load as use_assets
from filters import stroke, replace_color
from palette import BLACK, WHITE, BLUE
from config import TILE_SIZE, WINDOW_WIDTH
from sprite import Sprite
from town.actors.npc import Npc

def can_talk(hero, actor):
  if (not isinstance(actor, Npc)
  or not actor.messages
  or actor.core.faction == "player"):
    return False
  dist_x = actor.x - hero.x
  return abs(dist_x) < TILE_SIZE * 1.5 and dist_x * hero.facing > 0

def get_nearby_exits(hero, exits):
  for x in exits:
    dist_x = x - hero.x
    if abs(dist_x) < TILE_SIZE:
      return x

ARROW_PERIOD = 45
ARROW_BOUNCE = 2

class Area:
  bg_id = None
  width = WINDOW_WIDTH
  ACTOR_Y = 128

  def __init__(area):
    area.actors = []
    area.exits = []
    area.draws = 0

  def init(area, town):
    assets = use_assets()
    area.width = assets.sprites[area.bg_id].get_width()

  def render(area, hero):
    nodes = []
    assets = use_assets()
    bg_image = assets.sprites[area.bg_id]
    bg_x = -hero.x + WINDOW_WIDTH / 2
    if bg_x > 0:
      bg_x = 0
    if bg_x < -area.width + WINDOW_WIDTH:
      bg_x = -area.width + WINDOW_WIDTH
    nodes.append(Sprite(
      image=bg_image,
      pos=(bg_x, 0)
    ))
    arrow_image = assets.sprites["arrow_up"]
    bubble_image = assets.sprites["bubble_talk"]
    for actor in area.actors:
      sprite = actor.render()
      offset_x, offset_y = sprite.pos
      x = actor.x - TILE_SIZE // 2 + offset_x
      y = actor.y + Area.ACTOR_Y - 1 + offset_y
      if hero and can_talk(hero, actor):
        bubble_x = x + TILE_SIZE * 0.75 + 4
        bubble_y = y - TILE_SIZE * 0.25
        nodes.append(Sprite(
          image=bubble_image,
          pos=(bubble_x + bg_x, bubble_y)
        ))
      arrow_x = get_nearby_exits(hero, area.exits)
      if hero and arrow_x:
        arrow_x = arrow_x - TILE_SIZE // 2
        arrow_y = Area.ACTOR_Y + TILE_SIZE * 1.25
        arrow_y += sin(area.draws % ARROW_PERIOD / ARROW_PERIOD * 2 * pi) * ARROW_BOUNCE
        arrow_image = replace_color(arrow_image, BLACK, BLUE)
        nodes.append(Sprite(
          image=arrow_image,
          pos=(arrow_x + bg_x, arrow_y)
        ))
      nodes.append(Sprite(
        image=stroke(sprite.image, WHITE),
        pos=(x + bg_x, y)
      ))
    area.draws += 1
    return nodes
