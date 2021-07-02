from copy import deepcopy
from random import choice
from lib.cell import manhattan
from dungeon.features.specialroom import SpecialRoom
from dungeon.actors import DungeonActor
from dungeon.actors.eye import Eye as Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.props.door import Door
from dungeon.props.battledoor import BattleDoor
from anims.warpin import WarpInAnim
from anims.pause import PauseAnim

class ArenaRoom(SpecialRoom):
  Door = BattleDoor
  waves = [
    [Eyeball, Eyeball],
    # [Eyeball, Eyeball, Mushroom],
    # [Mushroom, Mushroom],
  ]

  def __init__(feature):
    super().__init__(degree=2, shape=[
      "   .   ",
      " ..... ",
      " ..... ",
      " ..... ",
      "   .   "
    ])
    feature.waves = deepcopy(ArenaRoom.waves)
    feature.entered = False

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [(x + feature.get_width() // 2, y + feature.get_height())]

  def get_doors(feature, stage):
    return [e for e in [stage.get_elem_at(c, superclass=Door) for c in feature.get_border()] if e]

  def get_enemies(feature, stage):
    return [e for e in [stage.get_elem_at(c, superclass=DungeonActor) for c in feature.get_cells()] if e and e.get_faction() == "enemy"]

  def effect(feature, game):
    return feature.on_enter(game)

  def spawn_wave(feature, game, wave):
    stage = game.floor
    hero = game.hero
    valid_cells = [c for c in feature.get_cells() if (
      stage.get_tile_at(c) is stage.FLOOR
      and manhattan(c, hero.cell) > 2
    )]
    i = 0
    while wave and valid_cells:
      enemy = wave.pop(0)()
      enemy_cell = choice(valid_cells)
      valid_cells.remove(enemy_cell)
      stage.spawn_elem_at(enemy_cell, enemy)
      anim = WarpInAnim(
        duration=15,
        delay=i * 10,
        target=enemy
      )
      if i:
        game.anims[-1].append(anim)
      else:
        game.anims.append([anim])
      i += 1

  def next_wave(feature, game):
    feature.spawn_wave(game, feature.waves.pop(0))

  def lock(feature, game):
    for door in feature.get_doors(game.floor):
      door.handle_close(game)

  def unlock(feature, game):
    for door in feature.get_doors(game.floor):
      door.handle_open(game)

  def on_enter(feature, game):
    if feature.entered:
      return False
    feature.entered = True
    feature.lock(game)
    feature.next_wave(game)
    return True

  def on_kill(feature, game, actor):
    if feature.get_enemies(game.floor):
      return False
    if feature.waves:
      feature.next_wave(game)
      for enemy in feature.get_enemies(game.floor):
        enemy.stepped = True
    else:
      game.anims.append([
        PauseAnim(
          duration=30,
          on_end=lambda: feature.unlock(game)
        )
      ])
    return True

  def place(feature, stage, *args, **kwargs):
    super().place(stage, *args, **kwargs)
    feat_x, feat_y = feature.cell
    top_edge = (feat_x + feature.get_width() // 2, feat_y - 1)
    stage.spawn_elem_at(top_edge, BattleDoor(locked=True))
    stage.set_tile_at(top_edge, stage.FLOOR)
