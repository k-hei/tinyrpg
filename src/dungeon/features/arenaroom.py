from random import choice
from lib.cell import manhattan
from dungeon.features.specialroom import SpecialRoom
from dungeon.actors.eye import Eye as Eyeball
from dungeon.props.door import Door
from dungeon.props.battledoor import BattleDoor
from anims.warpin import WarpInAnim

class ArenaRoom(SpecialRoom):
  Door = BattleDoor

  def __init__(feature):
    super().__init__(degree=2, shape=[
      "   .   ",
      " ..... ",
      " ..... ",
      " ..... ",
      "   .   "
    ])
    feature.entered = False

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [(x + feature.get_width() // 2, y + feature.get_height())]

  def get_doors(feature, stage):
    return [e for e in [stage.get_elem_at(c, superclass=Door) for c in feature.get_border()] if e]

  def effect(feature, game):
    return feature.on_enter(game)

  def spawn_wave(feature, game):
    stage = game.floor
    hero = game.hero
    valid_cells = [c for c in feature.get_cells() if (
      stage.get_tile_at(c) is stage.FLOOR
      and manhattan(c, hero.cell) > 2
    )]
    wave = [Eyeball, Eyeball, Eyeball]
    i = 0
    while wave and valid_cells:
      enemy_cell = choice(valid_cells)
      valid_cells.remove(enemy_cell)
      enemy = wave.pop()()
      stage.spawn_elem_at(enemy_cell, enemy)
      anim = WarpInAnim(
        duration=15,
        delay=30 + i * 10,
        target=enemy
      )
      if game.anims:
        game.anims[-1].append(anim)
      else:
        game.anims.append([anim])
      i += 1

  def on_enter(feature, game):
    if feature.entered:
      return False
    feature.entered = True
    for door in feature.get_doors(game.floor):
      door.close(game)
    feature.spawn_wave(game)
    return True
