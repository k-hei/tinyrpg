class Feature:
  def __init__(feature, degree=0, secret=False, on_place=None):
    feature.degree = degree
    feature.secret = secret
    feature.on_place = on_place

  def place(feature, stage, connectors=[], cell=None):
    for c in feature.get_cells():
      stage.set_tile_at(c, stage.FLOOR)
    feature.on_place and feature.on_place(feature, stage)
