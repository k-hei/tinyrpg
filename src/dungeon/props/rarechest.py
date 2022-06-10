from pygame import Rect
from dungeon.props import Prop
import assets
from lib.sprite import Sprite
from lib.filters import replace_color
import lib.vector as vector

from anims.shake import ShakeAnim
from anims.jump import JumpAnim
from anims.item import ItemAnim
from anims.frame import FrameAnim
from colors.palette import GOLD, BLACK
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from skills.ailment.virus import Virus


class RareChest(Prop):
  solid = True
  active = True
  static = True

  def __init__(chest, contents=None, opened=False, on_action=None):
    super().__init__()
    chest.contents = contents
    chest.opened = opened
    chest.on_action = on_action

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
      **(chest.opened and { "opened": chest.opened } or {}),
    }]

  def open(chest):
    contents = chest.contents
    chest.contents = None
    chest.opened = True
    return contents

  def effect(chest, game, *args, **kwargs):
    script = []
    contents = chest.contents
    success = False
    if contents:
      if game.store.obtain(contents) or contents is Virus:
        success = True
        game.camera.focus(
          target=chest,
          force=True,
        )
        game.get_tail().open(child=CutsceneContext(
          script=[
            lambda step: game.anims.extend([
              [FrameAnim(
                target=chest,
                duration=30,
                frames=assets.sprites["rarechest_opening"],
                on_end=chest.open
              )],
              [ShakeAnim(
                target=chest,
                magnitude=0.5,
                duration=60
              )],
              [
                JumpAnim(
                  target=chest,
                  on_start=lambda: (
                    contents is Virus and Virus.spawn_cloud(game, cell=chest.cell, on_end=step),
                  )
                ),
                *([item_anim := ItemAnim(
                  target=chest,
                  item=contents(),
                  on_start=lambda: game.get_tail().open(child=DialogueContext(
                    script=[("", ("Obtained ", contents().token(), "."))],
                    lite=True,
                  ), on_close=lambda: item_anim and item_anim.end()),
                  on_end=step
                )] if contents is not Virus else [])
              ]
            ]),
            lambda step: (
              chest.on_action(game.room, game, on_end=step) if chest.on_action else step()
            ),
            lambda step: (
              game.camera.blur(),
              step(),
            )
          ]
        ))
      else:
        script = ["Your inventory is already full!"]
    else:
      script = ["It's empty..."]
    if not success:
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
        chest_image = assets.sprites["rarechest_opened"]
      else:
        chest_image = assets.sprites["rarechest"]
    chest_image = replace_color(chest_image, BLACK, GOLD)
    return super().view([Sprite(
      image=chest_image
    )], anims)
