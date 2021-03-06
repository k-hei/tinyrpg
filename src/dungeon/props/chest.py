from pygame import Rect
from dungeon.props import Prop
import assets
import lib.vector as vector
from lib.cell import upscale
from lib.filters import replace_color
from anims.attack import AttackAnim
from anims.shake import ShakeAnim
from anims.jump import JumpAnim
from anims.item import ItemAnim
from anims.frame import FrameAnim
from colors.palette import PINK, GOLD, BLACK
from contexts.dialogue import DialogueContext
from lib.sprite import Sprite
from inventory import Inventory
from config import TILE_SIZE

class Chest(Prop):
  solid = True
  active = True

  def __init__(chest, contents=None, opened=False, rare=False):
    super().__init__()
    chest.contents = contents
    chest.opened = opened
    chest.rare = rare

  @property
  def rect(chest):
    if chest._rect is None and chest.pos:
      chest._rect = Rect(
        vector.add(chest.pos, (-10, -4)),
        (20, 20)
      )
    return chest._rect

  def encode(chest):
    [cell, kind, *props] = super().encode()
    return [cell, kind, {
      **(props[0] if props else {}),
      **(chest.contents and { "contents": chest.contents.__name__ } or {}),
      **(chest.opened and { "opened": True } or {}),
      **(chest.rare and { "rare": True } or {}),
    }]

  def open(chest):
    contents = chest.contents
    chest.contents = None
    chest.opened = True
    return contents

  def effect(chest, game, *_):
    anims = []
    script = []
    item = chest.contents
    item_anim = None
    success = False
    if item:
      if game.store.obtain(item):
        anims = [
          [JumpAnim(
            target=chest,
          ), FrameAnim(
            target=chest,
            duration=30,
            frames=assets.sprites["chest_opening"],
            on_end=chest.open
          ), item_anim := ItemAnim(
            target=chest,
            item=item()
          )]
        ]
        game.anims.append([
          ShakeAnim(
            target=chest,
            magnitude=0.5,
            duration=30,
            on_end=lambda: (
              game.anims.extend(anims),
              game.open(child=DialogueContext(
                lite=True,
                script=script
              ), on_close=lambda: (
                item_anim and item_anim.end(),
                game.camera.blur()
              ))
            )
          )
        ])
        script = [("", ("Obtained ", item().token(), "."))]
        success = True
      else:
        script = ["Your inventory is already full!"]
    else:
      script = ["It's empty..."]
    if anims:
      game.camera.focus(
        target=upscale(chest.cell, TILE_SIZE),
        force=True
      )
    else:
      game.open(child=DialogueContext(
        lite=True,
        script=script
      ))
    return success

  def view(chest, anims):
    anim_group = [a for a in anims[0] if a.target is chest] if anims else []
    for anim in anim_group:
      if type(anim) is FrameAnim:
        chest_image = anim.frame()
        break
    else:
      if chest.opened:
        chest_image = assets.sprites["chest_opened"]
      else:
        chest_image = assets.sprites["chest"]
    chest_color = PINK if chest.rare else GOLD
    chest_image = replace_color(chest_image, BLACK, chest_color)
    return super().view([Sprite(image=chest_image)], anims)
