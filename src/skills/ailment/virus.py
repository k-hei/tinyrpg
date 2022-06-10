from skills.ailment import AilmentSkill
from anims.bounce import BounceAnim
from cores.mage import Mage
from dungeon.props.puff_poison import PoisonPuff
from helpers.cloud import spawn_cloud as _spawn_cloud


class Virus(AilmentSkill):
    name: str = "Virus"
    desc: str = "Poisons adjacent targets"
    element: str = "dark"
    cost: int = 4
    users: tuple = (Mage,)
    blocks: tuple = (
        (0, 0),
        (1, 0),
        (1, 1),
    )
    charge_turns: int = 3

    def spawn_cloud(game, cell, inclusive=False, on_end=None):
        return _spawn_cloud(game, cell, puff_type=PoisonPuff, inclusive=inclusive, on_end=on_end)

    def effect(game, user, dest=None, on_start=None, on_end=None):
        spawn_cloud = lambda: Virus.spawn_cloud(
            game,
            cell=user.cell,
            on_end=on_end
        )

        if user.hp:
            game.anims.append([BounceAnim(
                target=user,
                on_start=lambda: on_start and on_start(),
                on_squash=spawn_cloud
            )])
        else:
            spawn_cloud()
