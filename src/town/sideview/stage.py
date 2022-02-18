from dataclasses import dataclass
import lib.vector as vector
from lib.filters import darken_image
from lib.sprite import Sprite
import assets
from contexts.dungeon.camera import Camera, CameraConstraints
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
  geometry = None
  camera_offset = (0, 0)
  actor_offset = 0
  buildings = []

  def __init__(area):
    area.actors = []
    area.camera = Camera(
      size=WINDOW_SIZE,
      offset=vector.add(
        area.camera_offset,
        (0, -area.actor_offset),
      )
    )
    area.draws = 0
    area.is_camera_locked = False

  def init(area, ctx):
    area.actors += area.buildings

  def spawn(area, actor, x, y=0):
    y = (actor.faction == "ally"
      and Area.NPC_Y - Area.ACTOR_Y + y
      or y)
    y += area.actor_offset
    actor.pos = (x, y)
    area.actors.append(actor)

  def lock_camera(area):
    area.camera.focus(area.camera.pos, force=True)
    area.is_camera_locked = True

  def update(area):
    area.camera.update()

  def view(area, hero, link):
    sprites = []

    if not area.camera.target:
      area.camera.focus(hero)

    area_bg_layers = [
      AreaBgLayer(sprite=Sprite(image=assets.sprites[area.bg], layer="bg"))
    ] if type(area.bg) is str else area.bg
    area.width = max([layer.sprite.image.get_width() for layer in area_bg_layers])
    area.camera.constraints = CameraConstraints(left=0, right=area.width)
    bg_sprites = [Sprite.move_all(
      sprites=[layer.sprite.copy()],
      offset=(
        (-area.camera.pos[0] + area.camera.size[0] / 2) * layer.scaling[0],
        -area.camera.pos[1]
      )
    )[0] for layer in area_bg_layers]
    sprites += bg_sprites

    if link:
      link_name = next((link_name for link_name, l in area.links.items() if l is link), None)
    else:
      link_name = None

    for actor in area.actors:
      sprites += actor.view()

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
