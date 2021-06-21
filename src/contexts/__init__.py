from pygame import Surface, SRCALPHA
from sprite import Sprite
from config import WINDOW_SIZE

class Context:
  effects = []

  def __init__(ctx, parent=None, on_close=None):
    ctx.on_close = on_close
    ctx.parent = parent
    ctx.child = None
    ctx.comps = []

  def get_root(ctx):
    if ctx.parent:
      return ctx.parent.get_root()
    else:
      return ctx

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)
    return False

  def handle_keyup(ctx, key):
    if ctx.child:
      return ctx.child.handle_keyup(key)
    return False

  def enter(ctx):
    pass

  def exit(ctx):
    pass

  def init(ctx):
    pass

  def open(ctx, child, on_close=None):
    ctx.child = child
    child.parent = ctx
    for kind in ctx.child.effects:
      for comp in ctx.comps:
        if isinstance(comp, kind):
          comp.exit()
    ctx.child.enter()
    child.init()
    if on_close:
      if child.on_close:
        on_close_old = child.on_close
        def close(data=None):
          on_close(on_close_old(data))
        child.on_close = close
      else:
        child.on_close = on_close
    return True

  def close(ctx, *args):
    ctx.parent.child = None
    for kind in ctx.effects:
      for comp in ctx.parent.comps:
        if isinstance(comp, kind):
          comp.enter()
    if ctx.on_close:
      ctx.on_close(*args)
    return True

  def update(ctx):
    if ctx.child:
      ctx.child.update()

  def view(ctx):
    return ctx.child.view() if ctx.child else []

  def draw(ctx, surface):
    if ctx.child:
      ctx.child.draw(surface)
