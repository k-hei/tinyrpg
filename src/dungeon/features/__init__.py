class Feature:
  def __init__(feature, degree=0, secret=False):
    feature.degree = degree
    feature.secret = secret

  def place(feature, stage):
    for cell in feature.get_cells():
      stage.set_tile_at(cell, stage.FLOOR)
