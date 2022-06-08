from town.sideview.stage import Area, AreaPort
from town.sideview.actor import Actor
from cores.genie import Genie
from helpers.npc import handle_menus
from assets import load as use_assets
from lib.sprite import Sprite
from config import TILE_SIZE, WINDOW_HEIGHT


class OutskirtsArea(Area):
  TOWER_X = 288

  name = "Outskirts"
  bg = "town_outskirts"
  ports = {
    "left": AreaPort(x=0, direction=(-1, 0)),
    "tower": AreaPort(x=TOWER_X - TILE_SIZE, direction=(1, 0)),
  }
  actor_offset = 28

  def init(area, ctx):
    super().init(ctx)
    GENIE_NAME = "Joshin"
    area.spawn(Actor(core=Genie(
      name=GENIE_NAME,
      facing=(-1, 0),
      message=handle_menus(GENIE_NAME),
    )), x=144)

  def view(area, hero, port):
    sprites = super().view(hero, port)
    assets = use_assets()
    sprite_bg = assets.sprites["town_outskirts"]
    sprite_tower = assets.sprites["tower"]
    sprites.append(Sprite(
      image=sprite_tower,
      pos=(OutskirtsArea.TOWER_X, Area.ACTOR_Y + area.actor_offset + WINDOW_HEIGHT / 2 - TILE_SIZE)
    ))
    return sprites
