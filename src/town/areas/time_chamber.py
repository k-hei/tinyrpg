from lib.sprite import Sprite
from lib.line import connect_lines
import assets
from cores.boar import Boar
from town.sideview.stage import Area, AreaBgLayer
from town.sideview.actor import Actor

BG_LAYERGROUP_OFFSET = (0, 28)

class TimeChamberArea(Area):
  name = "????"

  bg = [
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["time_chamber_roots"],
      layer="bg",
      pos=BG_LAYERGROUP_OFFSET,
    )),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["time_chamber_pillars"],
      layer="bg",
      pos=BG_LAYERGROUP_OFFSET,
    )),
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

  geometry = [
    *connect_lines([(48, 0), (112, 0), (248, 72), (520, 72), (656, 0), (720, 0)]),
  ]

  camera_lock = (False, True)
  camera_offset = (0, 28)
  actor_offset = 0

  def init(area, _):
    super().init(area)
    area.spawn(Actor(core=Boar(
      faction="enemy",
      facing=(1, 0),
      message=lambda _: [
        (Boar.name, "SKIN ME! FLAY ME! BURN ME ALIVE!"),
        (Boar.name, "I AIN'T GETTING IN THE DAMN BUBBLE BATH!!")
      ],
    )), x=456, y=72)
