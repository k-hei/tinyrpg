from lib.sprite import Sprite
from lib.line import connect_lines
import assets
from town.sideview.stage import Area, AreaBgLayer

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
