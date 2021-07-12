from dungeon.features.specialroom import SpecialRoom
from dungeon.actors import DungeonActor
from dungeon.actors.mage import Mage
from dungeon.props.battledoor import BattleDoor
from anims.pause import PauseAnim
from anims.path import PathAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.shake import ShakeAnim
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
import config
from config import WINDOW_HEIGHT, TILE_SIZE
from lib.cell import add as add_cell

class MageBossRoom(SpecialRoom):
  EntryDoor = BattleDoor
  ExitDoor = BattleDoor

  def __init__(room):
    super().__init__(degree=2, shape=[
      "#.....#",
      ".......",
      ".......",
      ".......",
      ".......",
      ".......",
      "#.....#"
    ], elems=[
      ((3, 2), mage := Mage(faction="ally", facing=(0, -1)))
    ])
    room.mage = mage

  def get_edges(room):
    x, y = room.cell or (0, 0)
    return [
      (x + room.get_width() // 2, y - 1),
      (x + room.get_width() // 2, y + room.get_height()),
      (x + room.get_width() // 2, y + room.get_height() + 1),
    ]

  def get_enemies(room, stage):
    return [e for e in [stage.get_elem_at(c, superclass=DungeonActor) for c in room.get_cells()] if e and e.get_faction() == "enemy"]

  def lock(room, game):
    for door in room.get_doors(game.floor):
      door.handle_close(game)

  def unlock(room, game):
    for door in room.get_doors(game.floor):
      door.handle_open(game)

  def on_enter(room, game):
    if room.entered:
      return False
    room.entered = True
    room.lock(game)
    game.anims.append([PauseAnim(
      duration=30,
      on_end=lambda: game.open(CutsceneContext(script=[
        *cutscene_setup(room, game),
        *(cutscene(room, game) if config.CUTSCENES else []),
        *cutscene_teardown(room, game),
      ]))
    )])
    return True

  def on_kill(room, game, actor):
    if room.get_enemies(game.floor):
      return False
    game.anims.append([
      PauseAnim(
        duration=15,
        on_end=lambda: room.on_complete(game)
      )
    ])
    return True

  def on_complete(room, game):
    room.unlock(game)
    game.anims.append([PauseAnim(duration=15)])

def cutscene_setup(room, game):
  return [
    lambda step: (
      game.camera.focus(room.get_center(), speed=8),
      game.hero.move_to(add_cell(room.cell, (3, 4))),
      game.anims.append([PathAnim(
        target=game.hero,
        path=[add_cell(room.cell, c) for c in [(3, 6), (3, 5), (3, 4)]],
        on_end=step
      )])
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      room.mage.set_facing((1, 0)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: (
      room.mage.set_facing((0, 1)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
  ]

def cutscene(room, game):
  knight = game.hero
  mage = room.mage
  return [
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.child.open(DialogueContext(script=[
      (mage.get_name(), "Won't you just stay dead and gone already!"),
      lambda: game.anims.append([JumpAnim(target=knight)]),
      (knight.get_name(), "Give me back my money! And my sword!"),
      (knight.get_name(), "And apologize for the inconveniences you have caused!"),
    ]), on_close=step),
    lambda step: game.anims.append([AttackAnim(
      target=mage,
      src=mage.cell,
      dest=add_cell(mage.cell, mage.get_facing()),
      on_end=step
    )]),
    lambda step: game.child.open(DialogueContext(script=[
      (mage.get_name(), "I'm NOT sorry I took those treasures."),
      (mage.get_name(), "I need them more than you!"),
      lambda: game.anims.append([JumpAnim(target=mage)]),
      (mage.get_name(), "Do you know the last time I had a piece of cheese? OR BREAD?"),
    ]), on_close=step),
    lambda step: game.anims.append([ShakeAnim(target=knight, duration=15, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.child.open(DialogueContext(script=[
      (knight.get_name(), "You did far more than just that!"),
      (mage.get_name(), "Why don't you leave me alone already!"),
      (mage.get_name(), "I'm not interested in being a captive of anyone else's again!"),
    ]), on_close=step),
    lambda step: game.anims.append([AttackAnim(
      target=knight,
      src=knight.cell,
      dest=add_cell(knight.cell, knight.get_facing()),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.child.open(DialogueContext(script=[
      (knight.get_name(), "Not only have you been trying to put me in the ground,"),
      (knight.get_name(), "you're permitless and exploring a tomb without permission."),
      (knight.get_name(), "A few years in a little box will give you enough time to think about everything you've done!"),
    ]), on_close=step),
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.child.open(DialogueContext(script=[
      (mage.get_name(), "Come and get me then, tin man!"),
    ]), on_close=step),
  ]

def cutscene_teardown(room, game):
  mage = room.mage
  return [
    lambda step: (
      mage.move_to(add_cell(room.cell, (3, 1))),
      game.anims.append([PathAnim(
        target=mage,
        path=[add_cell(room.cell, c) for c in [(3, 2), (3, 1)]],
        on_end=step
      )])
    ),
    lambda step: (
      room.mage.set_facing((1, 0)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: (
      room.mage.set_facing((0, 1)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      mage.set_faction("enemy"),
      step()
    )
  ]
