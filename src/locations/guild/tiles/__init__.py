from os import path
from locations.tileset import Tileset, RoomType
from config import LOCATIONS_PATH


class GuildTileset(Tileset):
    elems_path = path.join(LOCATIONS_PATH, "guild", "elems.json")
    room_type = RoomType.TOWN
