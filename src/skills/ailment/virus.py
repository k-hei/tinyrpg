from skills.ailment import AilmentSkill
from anims.bounce import BounceAnim
from anims.pause import PauseAnim
from dungeon.actors import DungeonActor
from cores.mage import Mage
from lib.cell import neighborhood
import locations.default.tileset as tileset
from dungeon.stage import Tile
from dungeon.props.poisonpuff import PoisonPuff

ATTACK_DURATION = 12

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
    target_area = neighborhood(cell, radius=2, inclusive=inclusive, predicate=lambda cell: (
      (not Tile.is_solid(game.stage.get_tile_at(cell)) or issubclass(game.stage.get_tile_at(cell), tileset.Pit))
      and not next((e for e in game.stage.get_elems_at(cell) if not isinstance(e, DungeonActor) and e.solid), None)
    ))
    targets = [e for e in game.stage.elems if (
      isinstance(e, DungeonActor)
      and not e.dead
      and e.ailment != "poison"
      and e.cell in target_area
    )]

    def poison():
      if targets:
        target = targets.pop()
      else:
        on_end and on_end()
        return
      game.inflict_poison(target, on_end=poison)

    for target_cell in target_area:
      existing_puff = next((e for e in game.stage.get_elems_at(target_cell) if isinstance(e, PoisonPuff) and not e.dissolving), None)
      if existing_puff:
        existing_puff.turns = PoisonPuff.MAX_TURNS
      else:
        game.stage.spawn_elem_at(target_cell, PoisonPuff(origin=cell))

    game.anims.extend([
      [PauseAnim(duration=30)],
      [PauseAnim(duration=1, on_end=poison)],
    ])

    return True

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
