# TODO: automate

from untiled.tilesets.desert import DesertProcessor
from untiled.tilesets.guild.processor import GuildProcessor


PROCESSOR_MAP = {
    "desert": DesertProcessor,
    "guild": GuildProcessor,
}


def resolve_processor(tileset_id):
    return (PROCESSOR_MAP[tileset_id]
        if tileset_id in PROCESSOR_MAP
        else None)
