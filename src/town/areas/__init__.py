from assets import load as use_assets
from filters import stroke
from palette import WHITE
from config import TILE_SIZE
from sprite import Sprite

from town.actors.npc import Npc

class Area:
  ACTOR_Y = 128

  def __init__(area):
    area.actors = []

  def render(area, hero=None):
    assets = use_assets()
    sprite_talkbubble = assets.sprites["bubble_talk"]
    nodes = []
    for actor in area.actors:
      sprite = actor.render()
      offset_x, offset_y = sprite.pos
      x = actor.x - TILE_SIZE // 2 + offset_x
      y = Area.ACTOR_Y - 1 + offset_y
      if isinstance(actor, Npc):
        y -= TILE_SIZE // 2
      if isinstance(actor, Npc) and actor.message and hero and can_talk(hero, actor):
        bubble_x = x + TILE_SIZE * 0.75
        bubble_y = y - TILE_SIZE * 0.25
        nodes.append(Sprite(
          image=sprite_talkbubble,
          pos=(bubble_x, bubble_y)
        ))
      nodes.append(Sprite(
        image=stroke(sprite.image, WHITE),
        pos=(x, y)
      ))
    return nodes

def can_talk(hero, actor):
  dist_x = actor.x - hero.x
  return abs(dist_x) < TILE_SIZE * 1.5 and dist_x * hero.facing > 0
