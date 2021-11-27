from lib.sprite import Sprite
import lib.vector as vector
from easing.expo import ease_out
import assets
from comps import Component
from comps.textbox import TextBox
from anims.tween import TweenAnim

class Minilog(Component):
  TEXTBOX_XPADDING = 22
  TEXTBOX_YPADDING = 12
  sprite = assets.sprites["minilog"]

  class EnterAnim(TweenAnim): duration = 15
  class ExitAnim(TweenAnim): duration = 7
  class WaitAnim(TweenAnim): duration = 180

  def __init__(log, *args, **kwargs):
    super().__init__(*args, **kwargs)
    log.message = None
    log.textbox = TextBox(size=(
      Minilog.sprite.get_width() - Minilog.TEXTBOX_XPADDING * 2,
      Minilog.sprite.get_height() - Minilog.TEXTBOX_YPADDING * 2
    ))
    log.anims = []
    log.exiting = True

  def enter(log, on_end=None):
    super().enter()
    log.anims = [
      Minilog.EnterAnim(on_end=on_end),
      Minilog.WaitAnim(on_end=log.exit),
    ]

  def exit(log, on_end=None):
    super().exit()
    log.anims = [Minilog.ExitAnim(on_end=on_end)]

  def print(log, message):
    log.message = message
    if log.anims and type(log.anims[0]) is Minilog.WaitAnim:
      log.anims[0].time = 0
      log.textbox.print(message)
    else:
      log.enter(on_end=lambda: log.textbox.print(message))

  def update(log):
    log_anim = log.anims[0] if log.anims else None
    if log_anim:
      if log_anim.done:
        log.anims.pop(0)
      log_anim.update()

  def view(log):
    log_image = assets.sprites["minilog"]
    log_height = log_image.get_height()
    log_anim = log.anims[0] if log.anims else None
    if type(log_anim) is Minilog.EnterAnim:
      log_height *= ease_out(log_anim.pos)
    elif type(log_anim) is Minilog.ExitAnim:
      log_height *= 1 - log_anim.pos
    elif type(log_anim) is not Minilog.WaitAnim and log.exiting:
      return []

    return [Sprite(
      image=log_image,
      pos=log.pos,
      size=(log_image.get_width(), log_height),
      origin=Sprite.ORIGIN_LEFT,
      layer="ui",
    ), *([Sprite(
      image=log.textbox.render(),
      pos=vector.add(log.pos, (Minilog.TEXTBOX_XPADDING, 0)),
      origin=Sprite.ORIGIN_LEFT,
      layer="ui",
    )] if log_anim and type(log_anim) is Minilog.WaitAnim else [])]
