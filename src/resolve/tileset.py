from tiles.default import mappings as default_mappings
from tiles.tomb import mappings as tomb_mappings

def resolve_tileset(key):
  if key == "default": return default_mappings
  if key == "tomb": return tomb_mappings
