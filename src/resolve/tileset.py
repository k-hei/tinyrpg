import tiles.tomb as tomb_tileset
import tiles.default as default_tileset

def resolve_tileset(key):
  if key == "tomb": return tomb_tileset
  if key == "default": return default_tileset
