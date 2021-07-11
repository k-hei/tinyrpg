from copy import deepcopy
from random import choice
from lib.cell import manhattan, neighborhood
from dungeon.features.specialroom import SpecialRoom
from dungeon.actors import DungeonActor
from dungeon.actors.eye import Eye as Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.props.door import Door
from dungeon.props.battledoor import BattleDoor
from dungeon.props.chest import Chest
from items.hp.elixir import Elixir
from anims.warpin import WarpInAnim
from anims.pause import PauseAnim
from anims.drop import DropAnim
from config import WINDOW_HEIGHT, TILE_SIZE

class ArenaRoom(SpecialRoom):
  EntryDoor = BattleDoor
  ExitDoor = BattleDoor
  waves = [
    [Eyeball, Eyeball],
    [Eyeball, Eyeball, Mushroom],
    [Mushroom, Mushroom],
  ]

  def __init__(feature, reward=Elixir):
    super().__init__(degree=2, shape=[
      "   .   ",
      "  ...  ",
      " ..... ",
      " ..... ",
      " ..... ",
      "  ...  ",
      "   .   "
    ])
    feature.reward = reward
    feature.waves = deepcopy(ArenaRoom.waves)
    feature.entered = False

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [
      (x + feature.get_width() // 2, y - 1),
      (x + feature.get_width() // 2, y + feature.get_height()),
      (x + feature.get_width() // 2, y + feature.get_height() + 1),
    ]

  def get_enemies(feature, stage):
    return [e for e in [stage.get_elem_at(c, superclass=DungeonActor) for c in feature.get_cells()] if e and e.get_faction() == "enemy"]

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

  def spawn_reward(feature, game):
    if feature.reward is None:
      return False
    spawn_x, spawn_y = feature.get_center()
    spawn_cell = (spawn_x, spawn_y)
    spawn_neighbors = neighborhood(spawn_cell)
    while game.floor.get_elem_at(spawn_cell) and spawn_neighbors:
      spawn_cell = spawn_neighbors.pop(0)
    if spawn_cell:
      reward = Chest(feature.reward)
      game.floor.spawn_elem_at(spawn_cell, reward)
      game.camera.focus(feature.get_center(), force=True)
      game.anims.append([DropAnim(
        target=reward,
        on_end=lambda: game.camera.blur()
      )])
      feature.reward = None
      return True
    else:
      return False

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
    game.anims.append([PauseAnim(
      duration=10,
      on_end=lambda: (
        game.camera.focus(feature.get_center(), force=True),
        game.anims.append([PauseAnim(
          duration=25,
          on_end=lambda: feature.next_wave(game)
        )])
      )
    )])
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
          on_end=lambda: feature.on_complete(game)
        )
      ])
    return True

  def on_complete(feature, game):
    feature.unlock(game)
    game.anims.append([PauseAnim(
      duration=15,
      on_end=lambda: feature.spawn_reward(game)
    )])
