class DungeonElement:
  def __init__(elem, solid=True, opaque=False):
    elem.solid = solid
    elem.opaque = opaque
    elem.cell = None

  def render(elem, sprite, anims=[]):
    return sprite
