from dungeon.actors.knight import Knight
from dungeon.actors.mage import Mage


def manifest_actor(core):
    core_id = type(core).__name__
    core_actors = {
        "Knight": Knight,
        "Mage": Mage,
    }
    return core_actors[core_id](core) if core_id in core_actors else None



from dataclasses import dataclass, field

@dataclass
class Spritesheet:
    _create_empty_facing_map = lambda: {
        (0, -1): None,
        (0, 1): None,
        (-1, 0): None,
        (1, 0): None,
    }

    idle: dict = field(default_factory=_create_empty_facing_map)
    move: dict = field(default_factory=_create_empty_facing_map)
    attack: dict = field(default_factory=_create_empty_facing_map)
    charge: any = None
    flinch: any = None

    @staticmethod
    def _normalize_facing(facing):
        return ((facing[0], 0)
            if facing[0] and facing[1]
            else facing)

    def get_idle_sprite(sgeet, facing):
        return sgeet.idle[sgeet._normalize_facing(facing)]

    def get_move_sprite(sgeet, facing):
        return sgeet.move[sgeet._normalize_facing(facing)]

    def get_attack_sprite(sgeet, facing):
        return sgeet.attack[sgeet._normalize_facing(facing)]

    def get_charge_sprites(sgeet):
        return sgeet.charge

    def get_flinch_sprite(sgeet):
        return sgeet.flinch
