class Context:
  def __init__(ctx, parent=None, on_close=None):
    ctx.child = None
    ctx.parent = parent
    ctx.on_close = on_close

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)
    return False

  def handle_keyup(ctx, key):
    if ctx.child:
      return ctx.child.handle_keyup(key)
    return False

  def close(ctx):
    ctx.parent.child = None
    if ctx.on_close:
      ctx.on_close()

  def draw(ctx, surface):
    if ctx.child:
      ctx.child.draw(surface)
