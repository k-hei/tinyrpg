from random import randint
from dungeon.props import Prop
from dungeon.actors import DungeonActor
import assets
from lib.filters import replace_color
from anims.item import ItemAnim
from items.gold import Gold
from contexts.dialogue import DialogueContext
from config import TILE_SIZE
from colors.palette import WHITE, COLOR_TILE, DARKBLUE
from lib.sprite import Sprite
from lib.cell import neighborhood
from anims.jump import JumpAnim

class Coffin(Prop):
  static = True
  solid = True

  def __init__(coffin, contents=None, locked=False):
    super().__init__()
    coffin.contents = contents
    coffin.locked = locked
    coffin.active = not locked
    coffin.unlocked = False
    coffin.opened = False

  def effect(coffin, game, *args, **kwargs):
    contents = coffin.contents
    script = None
    item_anim = None
    success = False
    if contents:
      if isinstance(contents, DungeonActor):
        coffin.open()
        neighbor = coffin.cell
        game.anims.append([JumpAnim(
          target=contents,
          src=coffin.cell,
          dest=neighbor,
          on_start=lambda: game.stage.spawn_elem_at(neighbor, contents)
        )])
      elif game.store.obtain(contents):
        coffin.open()
        if type(contents) is type:
          contents = contents()
        game.anims.append([
          item_anim := ItemAnim(
            target=coffin,
            item=contents
          )
        ])
        script = [("", ("Obtained ", contents.token(), "."))]
        success = True
      else:
        script = ["Your inventory is already full!"]
    else:
      script = ["It's empty..."]
    if script:
      game.open(child=DialogueContext(
        lite=True,
        script=script
      ), on_close=lambda: item_anim and item_anim.end())
    return success

  def unlock(coffin):
    coffin.locked = False
    coffin.active = True
    coffin.unlocked = True

  def open(coffin):
    coffin.opened = True
    contents = coffin.contents
    coffin.contents = None
    return contents

  def view(coffin, anims):
    if coffin.opened:
      coffin_image = assets.sprites["coffin_open"]
    else:
      coffin_image = assets.sprites["coffin"]
    coffin_color = DARKBLUE if coffin.unlocked else COLOR_TILE
    coffin_image = replace_color(coffin_image, WHITE, coffin_color)
    return super().view([Sprite(image=coffin_image, layer="tiles")], anims)

# class CoffinLid(Vfx):
#   def __init__(vfx, pos):
#     super().__init__(kind="coffin_lid", pos=pos)
