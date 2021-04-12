class Context:
  def __init__(ctx, parent=None):
    ctx.child = None
    ctx.parent = parent

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)
    return False

  def handle_keyup(ctx, key):
    if ctx.child:
      return ctx.child.handle_keyup(key)
    return False

  def render(ctx, surface):
    if ctx.child:
      ctx.child.render(surface)
