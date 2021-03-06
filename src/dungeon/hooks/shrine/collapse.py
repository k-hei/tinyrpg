import lib.vector as vector
from lib.cell import upscale
from contexts.cutscene import CutsceneContext
from anims.fall import FallAnim
from anims.pause import PauseAnim
from anims.shake import ShakeAnim
from dungeon.actors.mage import Mage
import locations.tomb.tiles as tileset
from config import TILE_SIZE, CUTSCENES

def on_collapse(room, game):
  game = (game if type(game).__name__ == "DungeonContext"
    else game.get_parent(cls="DungeonContext") or None)
  if game is None:
    raise TypeError(f"expected DungeonContext, got {game}")

  floor = game.stage
  hero = game.hero
  mage = floor.find_elem(Mage)
  altar = floor.find_elem(cls="Altar")
  if not altar:
    return False

  script = [
    lambda step: (
      game.camera.tween(
        target=upscale(vector.add(altar.cell, (0, 0.5)), game.stage.tile_size),
        on_end=lambda: (
          step()
        )
      )
    ),
    *[(lambda cell: lambda step: (
      floor.set_tile_at(vector.add(altar.cell, cell), tileset.Pit),
      game.redraw_tiles(force=True),
      game.anims.append([PauseAnim(duration=1, on_end=step)]),
    ))(c) for c in [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (1, 2), (0, 2), (-1, 2), (-1, 1), (-1, 0)]],
    lambda step: game.anims.append([PauseAnim(duration=30, on_end=step)]),
    lambda step: (
      game.anims.extend([
        [
          ShakeAnim(
            target=hero,
            duration=30,
            on_end=lambda: (
              game.anims[0].append(
                FallAnim(
                  target=hero,
                  y=hero.cell[1] * TILE_SIZE,
                  dest=(
                    (next( # TODO: refactor into `find_nearest_non_pit_cell(cell)` or `find_pit_depth(cell)`
                      (y for y in range(hero.cell[1], floor.height)
                        if not floor.is_tile_at_pit((hero.cell[0], y))
                      ),
                      floor.height
                    ) - hero.cell[1]) * TILE_SIZE
                  ),
                  on_end=lambda: floor.remove_elem(hero)
                )
              )
            )
          ),
          *(mage and [ShakeAnim(
            target=mage,
            duration=30,
            on_end=lambda: game.anims[0].append(
              FallAnim(
                target=mage,
                y=mage.cell[1] * TILE_SIZE,
                dest=(
                  (next(
                    (y for y in range(mage.cell[1], floor.height)
                      if not floor.is_tile_at_pit((mage.cell[0], y))
                    ),
                    floor.height
                  ) - mage.cell[1]) * TILE_SIZE
                ),
                on_end=lambda: floor.remove_elem(mage)
              )
            )
          )] or []),
          PauseAnim(duration=60)
        ],
        [PauseAnim(
          duration=30,
          on_end=step
        )]
      ])
    ),
    lambda step: game.load_floor_by_id(
      floor_id="Floor1",
      on_end=step,
    )
  ]

  if not isinstance(game.get_tail(), CutsceneContext):
    game.open(CutsceneContext(script))

  return script
