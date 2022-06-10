from random import randint
from dungeon.props.puff_cloud import CloudPuff
from colors.palette import WHITE, CYAN


class FreezingPuff(CloudPuff):
    max_turns = 7
    colors = (CYAN, WHITE)

    def effect(puff, game, trigger=None, on_end=None):
        if not super().effect(game, trigger, on_end):
            return False

        game.flinch(
            target=trigger,
            damage=randint(1, 2),
            on_end=on_end,
        )
        return True
