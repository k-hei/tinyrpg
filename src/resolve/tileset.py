import locations.prejungle.tiles as prejungle_tileset
import locations.tomb.tiles as tomb_tileset
from locations.desert.tiles import DesertTileset

def resolve_tileset(key):
  if key == "prejungle": return prejungle_tileset
  if key == "tomb": return tomb_tileset
  if key == "desert": return DesertTileset
