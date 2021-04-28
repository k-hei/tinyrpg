class DungeonElement:
  def __init__(elem, solid=True):
    elem.solid = solid
    elem.cell = None

  def render(elem, sprite, anims=[]):
    return sprite
