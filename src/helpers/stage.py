def find_tile(stage, tile):
  return next((c for c, t in stage.tiles.enumerate()
    if t == tile
    or t and isinstance(t, type) and isinstance(tile, type) and issubclass(t, tile)
  ), None)
