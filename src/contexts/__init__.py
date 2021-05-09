class Context:
  effects = []

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

  def open(ctx, child):
    ctx.child = child
    child.parent = ctx
    for kind in ctx.child.effects:
      for comp in ctx.comps:
        if isinstance(comp, kind):
          comp.exit()
    return True

  def close(ctx, data=None):
    ctx.parent.child = None
    for kind in ctx.effects:
      for comp in ctx.parent.comps:
        if isinstance(comp, kind):
          comp.enter()
    if ctx.on_close:
      ctx.on_close(data)
    return True

  def draw(ctx, surface):
    if ctx.child:
      ctx.child.draw(surface)
