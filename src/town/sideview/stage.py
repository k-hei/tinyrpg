from dataclasses import dataclass
from lib.filters import darken_image
from lib.sprite import Sprite
import assets
from config import WINDOW_WIDTH

@dataclass
class AreaLink:
  direction: tuple[int, int]
  x: int
  y: int = 0

@dataclass
class AreaBgLayer:
  sprite: Sprite
  scaling: tuple[float, float] = (1, 1)

class Area:
  ACTOR_Y = 136
  NPC_Y = 120
  DOOR_Y = 116
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

  def spawn(area, actor, x):
    y = (actor.faction == "ally"
      and Area.NPC_Y - Area.ACTOR_Y
      or 0)
    actor.pos = (x, y)
    area.actors.append(actor)

  def view(area, hero, link):
    sprites = []
    hero_x, _ = hero.pos

    area_bg_layers = [
      Sprite(image=assets.sprites[area.bg], layer="bg")
    ] if type(area.bg) is str else area.bg
    area.width = max([layer.sprite.image.get_width() for layer in area_bg_layers])
    area.camera = min(0, max(-area.width + WINDOW_WIDTH, -hero_x + WINDOW_WIDTH / 2))
    sprites += [Sprite.move_all(
      sprites=[layer.sprite.copy()],
      offset=(area.camera * layer.scaling[0], -24)
    )[0] for layer in area.bg]

    if link:
      link_name = next((link_name for link_name, l in area.links.items() if l is link), None)
    else:
      link_name = None
    for actor in sorted(area.actors, key=lambda actor: 1 if actor is hero else 0):
      try:
        actor_sprites = actor.view()
      except:
        actor_sprites = []
        raise
      for sprite in actor_sprites:
        y = Area.ACTOR_Y
        sprite.move((area.camera, y))
        sprite.target = actor
        _, sprite_y = sprite.pos
        if actor is hero and link_name and link_name.startswith("door") and sprite_y < Area.DOOR_Y:
          sprite.image = darken_image(sprite.image)
        sprites.append(sprite)
    if link_name and link_name.startswith("door"):
      link_pos = (link.x + area.camera, 96)
      sprites += [
        Sprite(
          image=assets.sprites["door_open"],
          pos=link_pos,
          origin=("center", "top"),
          layer="tiles"
        ),
        Sprite(
          image=assets.sprites["roof"],
          pos=link_pos,
          origin=("center", "bottom"),
          layer="fg"
        )
      ]
    sprites.sort(key=lambda sprite: sprite.depth(["bg", "tiles", "elems", "fg", "markers"]))
    return sprites
