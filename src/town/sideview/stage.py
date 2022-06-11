from dataclasses import dataclass
import lib.vector as vector
from lib.sprite import Sprite
from lib.filters import darken_image
import assets
from town.sideview.actor import Actor
from contexts.dungeon.camera import Camera, CameraConstraints
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE, TILE_SIZE

@dataclass
class AreaPort:
  direction: tuple[int, int]
  x: int
  y: int = 0
  door: bool = False
  lock_camera: bool = False

@dataclass
class AreaBgLayer:
  sprite: Sprite
  offset: tuple[float, float] = (0, 0)
  scaling: tuple[float, float] = (1, 1)

  def __post_init__(layer):
    if layer.scaling != (1, 1):
      layer.sprite.pos = vector.add(
        layer.sprite.pos,
        vector.multiply(
          layer.sprite.image.get_size(),
          vector.subtract((1, 1), layer.scaling),
          (-1 / 4, -1 / 4),
        ),
        layer.offset
      )

class MetaArea(type):
  def __hash__(area):
    return hash(area.key)

  def __str__(area):
    return str(area.key)

  @property
  def key(area):
    return area.__name__

class Area(metaclass=MetaArea):
  ACTOR_Y = 0
  NPC_Y = ACTOR_Y - 16
  DOOR_Y = ACTOR_Y - 20
  HORIZON_NORTH = -40
  TRANSIT_NORTH = -20
  HORIZON_SOUTH = 60
  TRANSIT_SOUTH = 30
  width = WINDOW_WIDTH
  name = "????"
  ports = {}
  bg = None
  geometry = None
  camera_lock = (False, False)
  camera_offset = (0, 0)
  camera_does_lock = True
  actor_offset = 0
  elems = []
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
    area.actors += area.elems

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

  def view(area, hero, port_id):
    sprites = []

    if not area.camera.target:
      area.camera.focus(hero)

    area_bg_layers = [
      AreaBgLayer(sprite=Sprite(image=assets.sprites[area.bg], layer="bg"))
    ] if type(area.bg) is str else area.bg
    area.width = max([layer.sprite.image.get_width() for layer in area_bg_layers])
    area.height = max([layer.sprite.image.get_height() for layer in area_bg_layers])

    if area.camera.constraints is None and area.camera_lock == (False, False):
      area.camera.constraints = CameraConstraints(right=area.width, top=-WINDOW_HEIGHT, bottom=area.height)

    elif area.camera.constraints is None and area.camera_lock == (False, True):
      area.camera.constraints = CameraConstraints(right=area.width)

    bg_sprites = [Sprite.move_all(
      sprites=[layer.sprite.copy()],
      offset=(
        (-area.camera.pos[0] + area.camera.size[0] / 2) * layer.scaling[0],
        -area.camera.pos[1] * layer.scaling[1]
      )
    )[0] for layer in area_bg_layers]
    sprites += bg_sprites

    port = area.ports[port_id] if port_id else None

    for actor in area.actors:
      actor_sprites = actor.view()

      if isinstance(actor, Actor) and actor.faction == "player":
        actor_sprite = actor_sprites[0]
        actor_sprite.offset += TILE_SIZE + (1 if actor is hero else 0)
        if (port_id and ("doorway" in port_id or port.door)
        and abs(actor.pos[1] - port.y) >= 16):
          actor_sprite.image = darken_image(actor_sprite.image)

      sprites += actor_sprites

    for sprite in sprites:
      if sprite not in bg_sprites:
        sprite.move(vector.negate(area.camera.rect.topleft))

    LAYER_SEQUENCE = ["bg", "tiles", "elems", "fg", "markers"]
    sprites.sort(key=lambda sprite: sprite.depth(LAYER_SEQUENCE) * WINDOW_HEIGHT + sprite.y)
    return sprites
