from random import randint
from dungeon.props import Prop
from dungeon.actors import DungeonActor
from vfx.puff_cloud import CloudPuffVfx
from colors.palette import VIOLET, DARKBLUE
from config import TILE_SIZE


class CloudPuff(Prop):
    max_turns = 7
    active = True
    transient = True

    def __init__(puff, origin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        puff.turns = CloudPuff.max_turns
        puff.origin = origin
        puff.vfx = None
        puff.dissolving = False
        puff.done = False

    def effect(puff, game, trigger=None, on_end=None):
        def end(success):
            if on_end:
                on_end()
            return success

        if puff.dissolving:
            return end(False)

        trigger = trigger or game.hero
        if not trigger or not isinstance(trigger, DungeonActor):
            return end(False)

        return True

    def dissolve(puff, *_):
        if puff.dissolving:
            return False
        puff.dissolving = True
        puff.turns = 0
        for i, fx in enumerate(puff.vfx):
            fx.dissolve(delay=i * 5, on_end=(lambda: (
                setattr(puff, "done", True)
            )) if fx == puff.vfx[-1] else None)

    def step(puff, *_):
        if puff.turns:
            puff.turns -= 1
        elif not puff.dissolving:
            puff.dissolve()

    def update(puff, *_):
        if puff.vfx:
            return []

        src = tuple([x * TILE_SIZE for x in puff.origin])
        dest = tuple([x * TILE_SIZE for x in puff.cell])

        create_puff_vfx = lambda size: CloudPuffVfx(
            src, dest,
            elev=puff.elev,
            colors=(VIOLET, DARKBLUE),
            size=size,
        )

        puff.vfx = (
            [create_puff_vfx(size="large") for _ in range(randint(3, 6))]
            + [create_puff_vfx(size="medium") for _ in range(randint(3, 6))]
            + [create_puff_vfx(size="small") for _ in range(randint(3, 6))]
            + [create_puff_vfx(size="tiny") for _ in range(randint(3, 6))]
        )
        return puff.vfx

    def view(puff, anims):
        return []
