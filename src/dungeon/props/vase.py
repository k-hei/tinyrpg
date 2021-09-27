import assets
from sprite import Sprite
from dungeon.props import Prop
from dungeon.props.itemdrop import ItemDrop
from colors.palette import WHITE, BLUE
from filters import replace_color
from anims.frame import FrameAnim
from anims.jump import JumpAnim
from anims.pause import PauseAnim
from anims.flicker import FlickerAnim

class Vase(Prop):
  solid = True
  active = True

  class OpenAnim(FrameAnim):
    frames = assets.sprites["vase_opening"]
    frames_duration = 5

  def __init__(vase, contents=None, opened=False):
    super().__init__()
    vase.contents = contents
    vase.opened = opened
    vase.anims = []

  def open(vase, game):
    if vase.opened:
      return None
    vase.opened = True
    vase.solid = False
    vase.active = False
    return vase.contents

  def effect(vase, game, *_):
    if vase.opened:
      return None
    item = vase.open(game)
    drop = ItemDrop(item)
    game.floor.spawn_elem_at(vase.cell, drop)
    not game.anims and game.anims.append([])
    game.anims[0] += [
      Vase.OpenAnim(target=vase),
      JumpAnim(target=drop, duration=20)
    ]
    vase.anims = [
      PauseAnim(duration=30),
      FlickerAnim(
        duration=45,
        on_end=lambda: game.floor.remove_elem(vase)
      )
    ]
    return True

  def update(vase, *_):
    if vase.anims:
      anim = vase.anims[0]
      if anim.done:
        vase.anims.pop(0)
      else:
        anim.update()

  def view(vase, anims=[], *args, **kwargs):
    if vase.opened:
      vase_image = assets.sprites["vase_opened"]
    else:
      vase_image = assets.sprites["vase"]
    anim_group = [a for a in anims[0] if a.target is vase] if anims else []
    anim_group += vase.anims
    for anim in anim_group:
      if isinstance(anim, FrameAnim):
        vase_image = anim.frame()
        break
      if isinstance(anim, PauseAnim):
        break
      if isinstance(anim, FlickerAnim) and not anim.visible:
        return super().view([], anims, *args, **kwargs)
    vase_image = replace_color(vase_image, (0xFF, 0x00, 0x00), BLUE)
    return super().view([Sprite(
      image=vase_image,
      layer="tiles" if vase.opened else "elems",
      offset=16 if vase.opened else 0
    )], anims, *args, **kwargs)
