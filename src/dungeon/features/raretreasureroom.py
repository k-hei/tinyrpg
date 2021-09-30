from random import shuffle
from lib.cell import add as add_vector
from dungeon.features.specialroom import SpecialRoom
from dungeon.features.room import Room
from dungeon.props.rarechest import RareChest
from dungeon.props.vcoffin import VCoffin
from dungeon.props.pillar import Pillar
from dungeon.props.raretreasuredoor import RareTreasureDoor
from dungeon.actors.mushroom import Mushroom
from skills.weapon.longinus import Longinus
from skills.ailment.virus import Virus
from anims.drop import DropAnim

class RareTreasureRoom(SpecialRoom):
  EntryDoor = RareTreasureDoor

  def __init__(feature):
    super().__init__(degree=1, shape=[
      "   ^^^^^^^   ",
      "   ^^^^^^^   ",
      "   ^^^^^^^   ",
      "   ^^^^^^^   ",
      "   ^^^^^^^   ",
      "   ^^^^^^^   ",
      "   ^^^^^^^   ",
      "      ^      ",
      "    ..^..    ",
      "   ..#^#..   ",
      "   ..^^^..   ",
      "   ./^^^\\.   ",
      "   ..^^^..   ",
      "   .......   ",
      "    .....    ",
      "      .      ",
    ], elems=[
      ((5, 0), VCoffin()),
      ((7, 0), VCoffin()),
      ((6, 3), RareChest(contents=Virus, on_action=feature.spawn_enemies)),
      ((4, 1), Pillar()),
      ((8, 1), Pillar()),
      ((4, 5), Pillar()),
      ((8, 5), Pillar()),
      ((3, 9), Pillar()),
      ((9, 9), Pillar(broken=True)),
      ((3, 13), Pillar()),
      ((9, 13), Pillar()),
    ])

  def spawn_enemies(feature, game, on_end=None):
    mushroom_anims = []
    mushroom_spawns = [(5, 6), (9, 4), (3, 2), (7, 1)]
    for i, spawn_point in enumerate(mushroom_spawns):
      mushroom = Mushroom(aggro=3)
      game.floor.spawn_elem_at(add_vector(feature.cell, spawn_point), mushroom)
      mushroom_anims.append(DropAnim(target=mushroom, delay=i * 10))
    mushroom_anims[-1].on_end = on_end
    game.anims.append(mushroom_anims)
    game.floor.spawn_elem_at(add_vector(feature.cell, (6, 11)), RareChest(contents=Longinus))

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [
      (x + 6, y + feature.get_height()),
      (x + 6, y + feature.get_height() + 1),
    ]
