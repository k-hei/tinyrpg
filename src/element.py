class Element:
  def __init__(elem, name=None):
    elem.name = name
    elem.cell = None

  def render(elem, sprite, anims=[]):
    return sprite