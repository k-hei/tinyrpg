from dataclasses import dataclass
import lib.vector as vector
from lib.filters import darken_image
from lib.sprite import Sprite
import assets
from contexts.dungeon.camera import Camera
from config import WINDOW_WIDTH, WINDOW_SIZE

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
  ACTOR_Y = 0
  NPC_Y = ACTOR_Y - 16
  DOOR_Y = ACTOR_Y - 20
  HORIZON_NORTH = -40
  TRANSIT_NORTH = -20
  HORIZON_SOUTH = 60
  TRANSIT_SOUTH = 30
  width = WINDOW_WIDTH
  bg = None

  def __init__(area):
    area.actors = []
    area.camera = Camera(size=WINDOW_SIZE, offset=(0, -32))
    area.draws = 0

  def init(area, ctx):
    pass

  def spawn(area, actor, x, y):
    y = (actor.faction == "ally"
      and Area.NPC_Y - Area.ACTOR_Y + y
      or y)
    actor.pos = (x, y)
    area.actors.append(actor)

  def update(area):
    area.camera.update()

  def view(area, hero, link):
    sprites = []
    hero_x, _ = hero.pos

    if not area.camera.target:
      area.camera.focus(hero)

    area_bg_layers = [
      Sprite(image=assets.sprites[area.bg], layer="bg")
    ] if type(area.bg) is str else area.bg
    area.width = max([layer.sprite.image.get_width() for layer in area_bg_layers])
    bg_sprites = [Sprite.move_all(
      sprites=[layer.sprite.copy()],
      offset=(
        (-area.camera.pos[0] + area.camera.size[0] / 2) * layer.scaling[0],
        -area.camera.pos[1]
      )
    )[0] for layer in area.bg]
    sprites += bg_sprites

    if link:
      link_name = next((link_name for link_name, l in area.links.items() if l is link), None)
    else:
      link_name = None

    for actor in area.actors:
      try:
        actor_sprites = actor.view()
      except:
        actor_sprites = []
        raise

      for sprite in actor_sprites:
        sprite.target = actor
        _, sprite_y = sprite.pos
        if actor is hero and link_name and link_name.startswith("door") and sprite_y < Area.DOOR_Y:
          sprite.image = darken_image(sprite.image)

      sprites += actor_sprites

    # TODO: refactor magic clause
    if link_name and link_name.startswith("door"):
      link_pos = (link.x, 96)
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

    for sprite in sprites:
      if sprite not in bg_sprites:
        sprite.move(vector.negate(area.camera.rect.topleft))

    LAYER_SEQUENCE = ["bg", "tiles", "elems", "fg", "markers"]
    sprites.sort(key=lambda sprite: sprite.depth(LAYER_SEQUENCE))
    return sprites
