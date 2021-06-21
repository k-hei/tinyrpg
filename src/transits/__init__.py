class Transit:
  def __init__(transit, on_end=None):
    transit.on_end = on_end
    transit.time = 0
    transit.done = False

  def update(transit):
    pass

  def view(transit, sprites=None):
    return []
