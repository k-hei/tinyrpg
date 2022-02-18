import lib.vector as vector
from lib.sprite import Sprite
from lib.line import connect_lines
import assets
from town.sideview.stage import Area, AreaBgLayer
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
      pos=vector.add(
        BG_LAYERGROUP_OFFSET,
        (-assets.sprites["time_chamber_roots"].get_width() * (1 - BG_LAYER_ROOTS_SCALING) / 4, 0)
      )
    ), scaling=(BG_LAYER_ROOTS_SCALING, 1)),
    AreaBgLayer(sprite=Sprite(
      image=assets.sprites["time_chamber_pillars"],
      layer="bg",
      pos=vector.add(
        BG_LAYERGROUP_OFFSET,
        (-assets.sprites["time_chamber_pillars"].get_width() * (1 - BG_LAYER_PILLARS_SCALING) / 4, 0)
      ),
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

  geometry = [
    *connect_lines([(48, 0), (112, 0), (248, 72), (520, 72), (656, 0), (720, 0)]),
  ]

  camera_lock = (False, True)
  camera_offset = (0, 28)

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

    area.spawn(Actor(core=Bunny(
      faction="enemy",
      facing=(-1, 0),
      message=lambda _: [
        (Bunny.name, "This is why I hate pigs..."),
      ],
    )), x=488, y=72)

    area.spawn(Actor(core=Mook(
      name=(mook_name := "Bingus"),
      faction="enemy",
      facing=(0, 1),
      message=lambda _: [
        (mook_name, "I'm so horny right now, I could make a brand new hole!"),
      ],
    )), x=344, y=72)
