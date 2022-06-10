from lib.cell import neighborhood
from dungeon.actors import DungeonActor
from dungeon.props.puff_cloud import CloudPuff
from anims.pause import PauseAnim
from config import TILE_SIZE


def spawn_cloud(game, cell, puff_type, radius=1, inclusive=False, on_end=None):
    target_cells = neighborhood(cell,
        radius=radius,
        inclusive=inclusive,
        predicate=lambda cell: (
            not game.stage.is_tile_at_solid(cell, scale=TILE_SIZE)
            and not next((e for e in game.stage.get_elems_at(cell, scale=TILE_SIZE)
                if not isinstance(e, DungeonActor) and e.solid), None)
        ))
    target_actors = [e for c in target_cells
        for e in game.stage.get_elems_at(c, scale=TILE_SIZE) if
            isinstance(e, DungeonActor) and not e.dead]

    # UNUSED: applies cloud effect to each actor sequentially
    def effect():
        if not target_actors:
            if on_end:
                on_end()
            return

        target_actor = target_actors.pop()
        existing_puff = next((e for e in game.stage.get_elems_at(target_actor.cell)
            if isinstance(e, CloudPuff)), None)
        if existing_puff:
            existing_puff.effect(game, trigger=target_actor, on_end=effect)

    for target_cell in target_cells:
        existing_puff = next((e for e in game.stage.get_elems_at(target_cell)
            if isinstance(e, CloudPuff) and not e.dissolving), None)
        if not existing_puff:
            game.stage.spawn_elem_at(target_cell, puff_type(origin=cell))

    game.anims.extend([
        [PauseAnim(duration=30)],
        [PauseAnim(duration=1, on_end=on_end)],
    ])

    return True
