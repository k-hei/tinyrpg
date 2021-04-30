class Feature:
  def __init__(feature):
    feature.degree = 0

  def place(feature, stage):
    for cell in feature.get_cells():
      stage.set_tile_at(cell, stage.FLOOR)
