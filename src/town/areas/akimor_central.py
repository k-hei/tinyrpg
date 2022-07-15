import lib.vector as vector
from lib.sprite import Sprite
from lib.line import connect_lines
import assets
from town.building import TownBuilding
from town.element import Element
from town.sideview.stage import Area, AreaPort, AreaBgLayer
from town.sideview.actor import Actor
from cores.mouse import Mouse
from config import WINDOW_HEIGHT

BG_LAYERGROUP_OFFSET = (0, -64)
FG_LAYERGROUP_OFFSET = (0, -52)
BUILDING_OFFSET = vector.add(FG_LAYERGROUP_OFFSET, (0, -WINDOW_HEIGHT / 2 + 4))
SPRITE_PREFIX = "akimor_central_"

class AkimorCentralArea(Area):
  name = "Akimor"

  bg = [
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["akimor_central_sky"],
      layer="bg",
      pos=BG_LAYERGROUP_OFFSET,
    ), scaling=(0.5, 1)),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["akimor_central_mountains"],
      layer="bg",
      pos=BG_LAYERGROUP_OFFSET,
    ), scaling=(0.75, 1)),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["akimor_central_cliffs"],
      layer="bg",
      pos=FG_LAYERGROUP_OFFSET,
    )),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["akimor_central_decors_rear"],
      layer="elems",
      pos=FG_LAYERGROUP_OFFSET,
    )),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["akimor_central_decors_front"],
      layer="fg",
      pos=FG_LAYERGROUP_OFFSET,
    )),
  ]

  buildings = [
    TownBuilding(
      sprite_id=f"{SPRITE_PREFIX}guild_house",
      pos=vector.add(BUILDING_OFFSET, (192, 160))
    ),
    TownBuilding(
      sprite_id=f"{SPRITE_PREFIX}npc_house",
      pos=vector.add(BUILDING_OFFSET, (80, 336))
    ),
    TownBuilding(
      sprite_id=f"{SPRITE_PREFIX}market",
      pos=vector.add(BUILDING_OFFSET, (368, 160)),
      offset=(0, 8),
    ),
    TownBuilding(
      sprite_id=f"{SPRITE_PREFIX}chapel",
      pos=vector.add(BUILDING_OFFSET, (688, 128))
    ),
    TownBuilding(
      sprite_id=f"{SPRITE_PREFIX}blacksmith",
      pos=vector.add(BUILDING_OFFSET, (208, 336)),
      offset=(0, 2),
    ),
    TownBuilding(
      sprite_id=f"{SPRITE_PREFIX}fortune_house",
      pos=vector.add(BUILDING_OFFSET, (352, 336))
    ),
    TownBuilding(
      sprite_id=f"{SPRITE_PREFIX}bar",
      pos=vector.add(BUILDING_OFFSET, (664, 336))
    ),
  ]

  elems = [
    Element(sprite=Sprite(
      image=assets.sprites[f"{SPRITE_PREFIX}market_doorway"],
      pos=(472, -68),
      origin=Sprite.ORIGIN_TOP,
      layer="fg",
    )),
    Element(sprite=Sprite(
      image=assets.sprites[f"{SPRITE_PREFIX}chapel_doorway"],
      pos=(744, -76),
      origin=Sprite.ORIGIN_TOP,
      layer="fg",
    )),
    Element(sprite=Sprite(
      image=assets.sprites[f"{SPRITE_PREFIX}blacksmith_doorway"],
      pos=(304, 132),
      origin=Sprite.ORIGIN_TOP,
      layer="fg",
    )),
  ]

  ports = {
    "left": AreaPort(x=0, y=0, direction=(-1, 0)),
    "right": AreaPort(x=1264, y=176, direction=(1, 0)),
    "upper_slope_top": AreaPort(x=608, y=0, direction=(0, 1)),
    "upper_slope_base": AreaPort(x=528, y=80, direction=(0, -1)),
    "lower_slope_top": AreaPort(x=608, y=80, direction=(0, 1)),
    "lower_slope_base": AreaPort(x=512, y=176, direction=(0, -1)),
    "guild_house_doorway": AreaPort(x=240, y=0, direction=(0, -1)),
    "market_doorway": AreaPort(x=472, y=0, direction=(0, -1)),
    "chapel_doorway": AreaPort(x=744, y=-32, direction=(0, -1)),
    "npc_house_doorway": AreaPort(x=112, y=176, direction=(0, -1)),
    "blacksmith_doorway": AreaPort(x=304, y=176, direction=(0, -1)),
    "fortune_house_doorway": AreaPort(x=408, y=176, direction=(0, -1)),
    "bar_doorway": AreaPort(x=768, y=176, direction=(0, -1)),
  }

  geometry = [
    *connect_lines([(0, 0), (608, 0), (608 + 64, -32), (608 + 64 + 160, -32)]),
    *connect_lines([(496, 80), (896, 80)]),
    *connect_lines([(0, 176), (1264, 176)]),
  ]

  camera_offset = (0, -32)

  def init(area, _):
    super().init(area)
    area.spawn(Actor(core=Mouse(
      faction="enemy",
      facing=(1, 0),
      message=lambda _: [
        (Mouse.name, "She was just like, I miss us :("),
        (Mouse.name, "And I was like, \"This user is currently building their crypto empire...\"")
      ],
    )), x=896, y=80)
