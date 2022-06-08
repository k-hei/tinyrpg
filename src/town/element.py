class Element:
  def __init__(elem, sprite):
    elem.sprite = sprite
    elem.message = None

  def update(elem):
    pass

  def view(elem):
    return [elem.sprite.copy()]
