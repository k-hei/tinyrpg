def find_tile(stage, tile):
  return next((c for c, t in stage.tiles.enumerate() if type(t) is type and issubclass(t, tile)), None)
