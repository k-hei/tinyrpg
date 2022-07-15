from lib.sprite import Sprite
import lib.vector as vector
from lib.line import connect_lines
import assets
from town.element import Element
from town.sideview.stage import Area, AreaPort, AreaBgLayer
from town.sideview.actor import Actor
from cores.boar import Boar
from cores.bunny import Bunny
from cores.mook import Mook

BG_LAYERGROUP_OFFSET = (0, 28)
BG_LAYER_ROOTS_SCALING = 0.8
BG_LAYER_PILLARS_SCALING = 0.9

class TimeChamberArea(Area):
  name = "????"

  bg = [
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["time_chamber_roots"],
      layer="bg",
      pos=BG_LAYERGROUP_OFFSET,
    ), scaling=(BG_LAYER_ROOTS_SCALING, 1)),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["time_chamber_pillars"],
      layer="bg",
      pos=BG_LAYERGROUP_OFFSET,
    ), scaling=(BG_LAYER_PILLARS_SCALING, 1)),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["time_chamber_pipes"],
      layer="bg",
      pos=BG_LAYERGROUP_OFFSET,
    )),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["time_chamber_wheel"],
      layer="bg",
      pos=BG_LAYERGROUP_OFFSET,
    )),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["time_chamber_sarcophagus"],
      layer="bg",
      pos=BG_LAYERGROUP_OFFSET,
    )),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["time_chamber_ground"],
      layer="bg",
      pos=BG_LAYERGROUP_OFFSET,
    )),
  ]

  elems = [
    Element(sprite=Sprite(
      image=assets.sprites["time_chamber_doorway_left"],
      pos=vector.add(BG_LAYERGROUP_OFFSET, (48, -12)),
      origin=Sprite.ORIGIN_BOTTOMRIGHT,
      layer="fg",
    )),
    Element(sprite=Sprite(
      image=assets.sprites["time_chamber_doorway_right"],
      pos=vector.add(BG_LAYERGROUP_OFFSET, (720, -12)),
      origin=Sprite.ORIGIN_BOTTOMLEFT,
      layer="fg",
    ))
  ]

  ports = {
    "left": AreaPort(x=48, y=0, direction=(-1, 0)),
    "right": AreaPort(x=720, y=0, direction=(1, 0)),
  }

  geometry = [
    *connect_lines([(48, 0), (112, 0), (248, 72), (520, 72), (656, 0), (720, 0)]),
  ]

  camera_lock = (False, True)
  camera_offset = (0, 28)

  def init(area, _):
    super().init(area)
    area._spawn_boar()
    area._spawn_bunny()
    area._spawn_mook()

  def _spawn_boar(area):
    area.spawn(Actor(core=Boar(
      faction="enemy",
      facing=(1, 0),
      message=lambda _: [
        (Boar.name, "SKIN ME! FLAY ME! BURN ME ALIVE!"),
        (Boar.name, "I AIN'T GETTING IN THE DAMN BUBBLE BATH!!")
      ],
    )), x=456, y=72)

  def _spawn_bunny(area):
    area.spawn(Actor(core=Bunny(
      faction="enemy",
      facing=(-1, 0),
      message=lambda _: [
        (Bunny.name, "This is why I hate pigs..."),
      ],
    )), x=488, y=72)

  def _spawn_mook(area):
    area.spawn(Actor(core=Mook(
      name=(mook_name := "Bingus"),
      faction="enemy",
      facing=(0, 1),
      message=lambda _: [
        (mook_name, "This time, I'm really gonna do it!"),
      ],
    )), x=344, y=72)
