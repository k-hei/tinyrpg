class Context:
  effects = []

  def __init__(ctx, parent=None, on_close=None):
    ctx.on_close = on_close
    ctx.parent = parent
    ctx.child = None
    ctx.comps = []

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

  def open(ctx, child, on_close=None):
    ctx.child = child
    child.parent = ctx
    for kind in ctx.child.effects:
      for comp in ctx.comps:
        if isinstance(comp, kind):
          comp.exit()
    ctx.child.enter()
    if on_close:
      on_close_old = child.on_close
      def close(data=None):
        on_close_old(data)
        on_close(data)
      child.on_close = close
    return True

  def close(ctx, data=None):
    ctx.parent.child = None
    for kind in ctx.effects:
      for comp in ctx.parent.comps:
        if isinstance(comp, kind):
          comp.enter()
    if ctx.on_close:
      if data is None:
        ctx.on_close()
      else:
        ctx.on_close(data)
    return True

  def update(ctx):
    pass

  def draw(ctx, surface):
    if ctx.child:
      ctx.child.draw(surface)
