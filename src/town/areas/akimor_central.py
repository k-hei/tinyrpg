import assets
from lib.sprite import Sprite
from lib.line import connect_lines
from town.sideview.stage import Area, AreaLink, AreaBgLayer

class AkimorCentralArea(Area):
  name = "Akimor"
  bg = [
    AreaBgLayer(sprite=Sprite(image=assets.sprites["akimor_central_sky"], layer="bg")),
    AreaBgLayer(sprite=Sprite(image=assets.sprites["akimor_central_mountains"], layer="bg"), scaling=(0.75, 1)),
    AreaBgLayer(sprite=Sprite(image=assets.sprites["akimor_central_cliffs"], layer="bg")),
    AreaBgLayer(sprite=Sprite(image=assets.sprites["akimor_central_buildings"], layer="bg")),
    AreaBgLayer(sprite=Sprite(image=assets.sprites["akimor_central_decors_rear"], layer="bg")),
    AreaBgLayer(sprite=Sprite(image=assets.sprites["akimor_central_decors_front"], layer="fg")),
  ]
  links = {
    "upper_slope_top": AreaLink(x=608, y=0, direction=(0, 1)),
    "upper_slope_base": AreaLink(x=528, y=80, direction=(0, -1)),
    "lower_slope_top": AreaLink(x=608, y=80, direction=(0, 1)),
    "lower_slope_base": AreaLink(x=528, y=160, direction=(0, -1)),

  }
  geometry = [
    *connect_lines([(0, 0), (608, 0), (608 + 64, -32), (608 + 64 + 160, -32)])
  ]
