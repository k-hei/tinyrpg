from assets import load as use_assets
from filters import stroke
import palette
import config

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
      sprite, x, y = actor.render()
      sprite = stroke(sprite, palette.WHITE)
      x = x + actor.x - config.TILE_SIZE // 2
      y = y + Area.ACTOR_Y - 1
      if isinstance(actor, Npc):
        y -= config.TILE_SIZE // 2
      if isinstance(actor, Npc) and actor.message and hero and can_talk(hero, actor):
        bubble_x = x + config.TILE_SIZE * 0.75
        bubble_y = y - config.TILE_SIZE * 0.25
        nodes.append((sprite_talkbubble, (bubble_x, bubble_y)))
      nodes.append((sprite, (x, y)))
    return nodes

def can_talk(hero, actor):
  dist_x = actor.x - hero.x
  return abs(dist_x) < config.TILE_SIZE * 1.5 and dist_x * hero.facing > 0
