import lib.vector as vector
from lib.cell import upscale
from contexts.cutscene import CutsceneContext
from dungeon.actors.mage import Mage
from anims.pause import PauseAnim
from anims.path import PathAnim
from anims.attack import AttackAnim
from config import MOVE_DURATION
import config

def on_focus(room, game):
  door = room.get_doors(game.stage)[0]
  mage = next((e for c in room.cells for e in game.stage.get_elems_at(c) if isinstance(e, Mage)), None)
  if not mage:
    return

  if not config.CUTSCENES or "minxia" in game.store.story:
    game.stage.remove_elem(mage)
    return

  game.get_tail().open(CutsceneContext([
    lambda step: (
      setattr(mage, "facing", (-1, 0)),
      game.camera.tween(
        target=upscale(mage.cell, game.stage.tile_size),
        duration=1,
      ),
      game.anims.append([PauseAnim(duration=30, on_end=step)])
    ),
    lambda step: (
      setattr(mage, "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=30, on_end=step)])
    ),
    lambda step: (
      setattr(mage, "facing", (0, -1)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: (
      setattr(mage, "facing", (-1, 0)),
      game.anims.append([PauseAnim(duration=30, on_end=step)])
    ),
    lambda step: (
      setattr(mage, "facing", (0, -1)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: (
      game.anims.append([
        PathAnim(
          target=mage,
          path=game.stage.pathfind(
            start=mage.cell,
            goal=(goal_cell := vector.add(door.cell, (0, 1)))
          ),
          on_end=lambda: (
            setattr(mage, "cell", goal_cell),
            step()
          )
        )
      ])
    ),
    lambda step: (
      game.anims.extend([
        [PauseAnim(duration=5)],
        [AttackAnim(
          target=mage,
          src=mage.cell,
          dest=vector.add(mage.cell, mage.facing),
          on_connect=lambda: door.handle_open(game)
        )],
        [PauseAnim(duration=5)],
        [PathAnim(
          target=mage,
          path=(path := [
            mage.cell,
            vector.add(mage.cell, (0, -1)),
            vector.add(mage.cell, (0, -2)),
          ]),
          on_end=lambda: (
            setattr(mage, "cell", path[-1]),
            door.handle_close(game, lock=None),
            game.stage.remove_elem(mage),
            step()
          )
        )]
      ])
    ),
    lambda step: (
      game.camera.blur(),
      setattr(game.hero, "facing", (0, -1)),
      step()
    )
  ]))
