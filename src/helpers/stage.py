def find_tile(stage, tile):
  return next((c for c, t in stage.tiles.enumerate() if issubclass(t, tile)), None)
