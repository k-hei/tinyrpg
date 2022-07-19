import locations.prejungle.tiles as prejungle_tileset
from locations.tomb.tiles import TombTileset
from locations.desert.tiles import DesertTileset
from locations.guild.tiles import GuildTileset

def resolve_tileset(key):
  if key == "prejungle": return prejungle_tileset
  if key == "tomb": return TombTileset
  if key == "desert": return DesertTileset
  if key == "guild": return GuildTileset
