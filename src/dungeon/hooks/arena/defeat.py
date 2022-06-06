from random import shuffle
from lib.cell import manhattan, neighborhood, upscale
from anims.pause import PauseAnim
from anims.warpin import WarpInAnim
from anims.drop import DropAnim
from contexts.cutscene import CutsceneContext
from dungeon.props.chest import Chest
from items.hp.elixir import Elixir

def on_defeat(room, game, actor):
  enemies = [e for e in room.get_enemies(game.stage) if e is not actor]
  if actor.faction != "enemy" or game.room is not room:
    return True

  if not enemies:
    if room.waves:
      spawn_next_wave(room, game)
    else:
      on_complete(room, game)

  return True

def on_complete(room, game):
  door = sorted(room.get_doors(game.stage), key=lambda d: d.cell[1])[0]
  game.get_tail().open(CutsceneContext(script=[
    lambda step: (
      game.camera.focus(
        target=upscale(door.cell, game.stage.tile_size),
        force=True
      ),
      game.anims.append([
        PauseAnim(
          duration=45,
          on_end=lambda: (
            room.unlock(game, open=True),
            game.anims.append([PauseAnim(duration=45, on_end=step)])
          ),
        )
      ])
    ),
    lambda step: (
      game.camera.focus(
        target=upscale(room.center, game.stage.tile_size),
        force=True
      ),
      game.anims.append([PauseAnim(duration=30, on_end=step)])
    ),
    lambda step: (
      game.stage.spawn_elem_at(next((
        c for c in neighborhood(
          cell=room.center,
          inclusive=True,
          radius=2
        ) if game.stage.is_cell_empty(c)
      ), room.center), chest := Chest(Elixir)),
      game.anims.extend([
        [DropAnim(target=chest)],
        [PauseAnim(duration=15, on_end=step)]
      ])
    ),
    lambda step: (
      game.camera.blur(),
      game.camera.blur(),
      game.exit(),
      step(),
    )
  ]))

def spawn_next_wave(room, game):
  enemy_types = room.waves.pop(0)
  valid_cells = [c for c in room.cells if (
    game.stage.is_cell_empty(c)
    and manhattan(c, game.hero.cell) > 2
    and manhattan(c, game.hero.cell) <= 5
    and len(game.stage.pathfind(
      start=c,
      goal=game.hero.cell
    )) <= 8
  )]
  shuffle(valid_cells)
  enemy_spawns = {}
  while enemy_types and valid_cells:
    enemy = enemy_types.pop(0)(aggro=1)
    cell = valid_cells.pop(0)
    enemy_spawns[cell] = enemy

  not game.anims and game.anims.append([PauseAnim(duration=30)])
  for i, (cell, enemy) in enumerate(enemy_spawns.items()):
    game.stage.spawn_elem_at(cell, enemy)
    game.anims[0].append(WarpInAnim(
      target=enemy,
      delay=i * 15
    ))
