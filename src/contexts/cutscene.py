from pygame import Surface
from contexts import Context
from anims.tween import TweenAnim
from colors.palette import BLACK
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from sprite import Sprite
from easing.expo import ease_out

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

class CutsceneContext(Context):
  BAR_HEIGHT = 24

  def __init__(ctx, script, *args, **kwargs):
    super().__init__(ctx, *args, **kwargs)
    ctx.script = script
    ctx.script_idx = -1
    ctx.anim = TweenAnim(duration=30)
    ctx.cache_bar = None

  def init(ctx):
    ctx.cache_bar = Surface((WINDOW_WIDTH, CutsceneContext.BAR_HEIGHT))
    ctx.cache_bar.fill(BLACK)
    if callable(ctx.script):
      ctx.script = ctx.script(ctx.parent)
    ctx.next()

  def next(ctx):
    ctx.script_idx += 1
    if ctx.script_idx == len(ctx.script):
      ctx.exit()
    elif ctx.script[ctx.script_idx]:
      ctx.script[ctx.script_idx](ctx.next)
    else:
      ctx.next()

  def enter(ctx):
    ctx.anim = EnterAnim(duration=15)

  def exit(ctx, on_end=None):
    ctx.anim = ExitAnim(duration=7, on_end=lambda: (
      on_end and on_end(),
      ctx.close()
    ))

  def update(ctx):
    super().update()
    if ctx.anim:
      if ctx.anim.done:
        ctx.anim = None
      else:
        ctx.anim.update()

  def view(ctx):
    sprites = []
    bar_height = CutsceneContext.BAR_HEIGHT
    if ctx.anim:
      t = ctx.anim.pos
      if type(ctx.anim) is EnterAnim:
        t = ease_out(t)
      elif type(ctx.anim) is ExitAnim:
        t = 1 - t
      bar_height *= t
    sprites += [
      Sprite(
        image=ctx.cache_bar,
        pos=(0, 0),
        size=(WINDOW_WIDTH, bar_height),
        layer="ui"
      ),
      Sprite(
        image=ctx.cache_bar,
        pos=(0, WINDOW_HEIGHT),
        size=(WINDOW_WIDTH, bar_height),
        origin=("left", "bottom"),
        layer="ui"
      )
    ]
    return sprites + super().view()
