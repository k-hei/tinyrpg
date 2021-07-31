class Feature:
  def __init__(feature, degree=0, secret=False, placed=False, on_place=None):
    feature.degree = degree
    feature.secret = secret
    feature.placed = placed
    feature.on_place = on_place

  def get_edges(maze):
    return []

  def get_entrances(feature):
    return feature.get_edges()

  def get_exits(feature):
    return feature.get_edges()

  def place(feature, stage, cell=None, connectors=[]):
    if feature.placed:
      return False
    for c in feature.get_cells():
      stage.set_tile_at(c, stage.FLOOR)
    feature.on_place and feature.on_place(feature, stage)
    return True
