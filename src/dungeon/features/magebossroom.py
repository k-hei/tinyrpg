from dungeon.features.specialroom import SpecialRoom
from dungeon.actors import DungeonActor
from dungeon.props.battledoor import BattleDoor
from anims.pause import PauseAnim
from config import WINDOW_HEIGHT, TILE_SIZE

class MageBossRoom(SpecialRoom):
  EntryDoor = BattleDoor
  ExitDoor = BattleDoor

  def __init__(feature):
    super().__init__(degree=2, shape=[
      "#.....#",
      ".......",
      ".......",
      ".......",
      ".......",
      ".......",
      "#.....#"
    ])

  def get_edges(feature):
    x, y = feature.cell or (0, 0)
    return [
      (x + feature.get_width() // 2, y - 1),
      (x + feature.get_width() // 2, y + feature.get_height()),
      (x + feature.get_width() // 2, y + feature.get_height() + 1),
    ]

  def get_enemies(feature, stage):
    return [e for e in [stage.get_elem_at(c, superclass=DungeonActor) for c in feature.get_cells()] if e and e.get_faction() == "enemy"]

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
    game.anims.append([PauseAnim(duration=10)])
    return True

  def on_kill(feature, game, actor):
    if feature.get_enemies(game.floor):
      return False
    game.anims.append([
      PauseAnim(
        duration=30,
        on_end=lambda: feature.on_complete(game)
      )
    ])
    return True

  def on_complete(feature, game):
    feature.unlock(game)
    game.anims.append([PauseAnim(duration=15)])
