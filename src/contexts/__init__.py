from pygame import Surface, SRCALPHA
from lib.sprite import Sprite
from config import WINDOW_SIZE

class Context:
  def __init__(ctx, parent=None, on_close=None):
    ctx.on_close = on_close
    ctx.parent = parent
    ctx.child = None
    ctx.comps = []

  def get_head(ctx):
    return ctx.parent.get_head() if ctx.parent else ctx

  def get_tail(ctx):
    return ctx.child.get_tail() if ctx.child else ctx

  def get_parent(ctx, cls=None):
    if not ctx.parent:
      return None
    if not cls:
      return ctx.parent
    if (type(ctx.get_parent()) is cls
    or type(cls) is str and type(ctx.get_parent()).__name__ == cls):
      return ctx.get_parent()
    return ctx.get_parent().get_parent(cls)

  def get_depth(ctx, depth=0):
    if ctx.child:
      return ctx.child.get_depth(depth + 1)
    else:
      return depth

  def handle_press(ctx, key):
    if ctx.child:
      return ctx.child.handle_press(key)

  def handle_release(ctx, key):
    if ctx.child:
      return ctx.child.handle_release(key)

  def enter(ctx):
    pass

  def exit(ctx):
    pass

  def init(ctx):
    pass

  def open(ctx, child, on_close=None):
    ctx.child = child
    child.parent = ctx
    ctx.child.enter()
    child.init()
    if on_close:
      if child.on_close:
        on_close_old = child.on_close
        child.on_close = lambda *data: (
          on_close(on_close_old(*data)),
        )
      else:
        child.on_close = on_close
    return True

  def close(ctx, *args):
    if ctx.child:
      ctx.child.close()
    if ctx.parent:
      ctx.parent.child = None
    if ctx.on_close:
      ctx.on_close(*args)
    return True

  def update(ctx):
    if ctx.child:
      try:
        ctx.child.update()
      except:
        raise

  def view(ctx):
    return ctx.child.view() if ctx.child else []

  def draw(ctx, surface):
    if ctx.child:
      ctx.child.draw(surface)
