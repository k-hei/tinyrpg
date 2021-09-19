from dungeon.features.specialroom import SpecialRoom
from dungeon.actors import DungeonActor
from dungeon.actors.mage import Mage
from dungeon.props.battledoor import BattleDoor
from anims.pause import PauseAnim
from anims.path import PathAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.shake import ShakeAnim
from anims.flicker import FlickerAnim
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
import config
from config import WINDOW_HEIGHT, TILE_SIZE
from lib.cell import add as add_cell
from skills.weapon.broadsword import BroadSword

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
    ])
    room.mage = None

  def get_edges(room):
    x, y = room.cell or (0, 0)
    return [
      (x + room.get_width() // 2, y - 1),
      (x + room.get_width() // 2, y + room.get_height()),
      (x + room.get_width() // 2, y + room.get_height() + 1),
    ]

  def get_enemies(room, stage):
    return [e for e in [stage.get_elem_at(c, superclass=DungeonActor) for c in room.get_cells()] if (
      e and e.faction == "enemy"
    )]

  def on_focus(room, game):
    if not super().on_focus(game) or "minxia" in game.store.story:
      return False
    room.mage = Mage(
      faction="ally",
      facing=(0, -1)
    )
    game.floor.spawn_elem_at(add_cell(room.cell, (3, 2)), room.mage)
    return True

  def on_enter(room, game):
    if not super().on_enter(game) or "minxia" in game.store.story:
      return False
    room.lock(game)
    game.anims.append([PauseAnim(
      duration=30,
      on_end=lambda: game.open(CutsceneContext(script=[
        *prebattle_cutscene_setup(room, game),
        *(prebattle_cutscene(room, game) if config.CUTSCENES else []),
        *prebattle_cutscene_teardown(room, game),
      ]))
    )])
    return True

  def on_defeat(room, game, actor):
    if actor is room.mage:
      room.on_complete(game)
      return False
    return True

  def on_complete(room, game):
    game.store.story.append("minxia")
    game.anims.append([PauseAnim(
      duration=30,
      on_end=lambda: game.open(CutsceneContext(
        script=[
          *postbattle_cutscene_setup(room, game),
          *(postbattle_cutscene(room, game) if config.CUTSCENES else []),
          *postbattle_cutscene_teardown(room, game),
          lambda step: (
            room.unlock(game),
            step()
          )
        ]
      ))
    )])

def prebattle_cutscene_setup(room, game):
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
      setattr(room.mage, "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: (
      setattr(room.mage, "facing", (0, 1)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
  ]

def prebattle_cutscene(room, game):
  knight = game.hero
  mage = room.mage
  return [
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.child.open(DialogueContext(script=[
      (mage.name, "Won't you just stay dead and gone already!"),
      lambda: game.anims.append([JumpAnim(target=knight)]),
      (knight.name, "Give me back my money! And my sword!"),
      (knight.name, "And apologize for the inconveniences you have caused!"),
    ]), on_close=step),
    lambda step: game.anims.append([AttackAnim(
      target=mage,
      src=mage.cell,
      dest=add_cell(mage.cell, mage.facing),
      on_end=step
    )]),
    lambda step: game.child.open(DialogueContext(script=[
      (mage.name, "I'm NOT sorry I took those treasures."),
      (mage.name, "I need them more than you!"),
      lambda: game.anims.extend([
        [PauseAnim(duration=5)],
        [PathAnim(
          target=mage,
          path=[add_cell(room.cell, c) for c in [(3, 2), (2, 2), (3, 2), (4, 2), (3, 2)]],
          on_end=lambda: mage.face(knight.cell)
        )],
        [JumpAnim(target=mage)]
      ]),
      (mage.name, "Do you know the last time I had a piece of cheese? OR BREAD?"),
    ]), on_close=step),
    lambda step: game.anims.append([ShakeAnim(target=knight, duration=30, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.child.open(DialogueContext(script=[
      (knight.name, "You did far more than just that!"),
      (mage.name, "Why don't you leave me alone already!"),
      (mage.name, "I'm not interested in being a captive of anyone else's again!"),
    ]), on_close=step),
    lambda step: game.anims.append([AttackAnim(
      target=knight,
      src=knight.cell,
      dest=add_cell(knight.cell, knight.facing),
      on_end=step
    )]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.child.open(DialogueContext(script=[
      (knight.name, "Not only have you been trying to put me in the ground,"),
      (knight.name, "you're permitless and exploring a tomb without permission."),
      (knight.name, "A few years in a little box will give you enough time to think about everything you've done."),
    ]), on_close=step),
    lambda step: (
      setattr(room.mage, "facing", (-1, 0)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: (
      setattr(room.mage, "facing", (0, -1)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: (
      setattr(room.mage, "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: (
      setattr(room.mage, "facing", (0, 1)),
      game.anims.append([PauseAnim(duration=5, on_end=step)])
    ),
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=10, on_end=step)]),
    lambda step: game.child.open(DialogueContext(script=[
      (mage.name, "Come and get me then, tin man!!"),
    ]), on_close=step),
  ]

def prebattle_cutscene_teardown(room, game):
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
      setattr(room.mage, "facing", (1, 0)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: (
      setattr(room.mage, "facing", (0, 1)),
      game.anims.append([PauseAnim(duration=10, on_end=step)])
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      setattr(mage, "faction", "enemy"),
      step()
    )
  ]

def postbattle_cutscene_setup(room, game):
  mage = room.mage
  return [
    lambda step: (
      mage.revive(hp_factor=0),
      enemies := [e for e in room.get_enemies(game.floor) if e is not mage],
      game.anims.extend([
        [(lambda e: FlickerAnim(
          target=e,
          duration=45,
          on_end=lambda: game.floor.remove_elem(e)
        ))(e) for e in enemies],
        [PauseAnim(duration=15, on_end=step)]
      ]) if enemies else step()
    )
  ]

def postbattle_cutscene(room, game):
  knight = game.hero
  mage = room.mage
  midpoint = (
    (knight.cell[0] + mage.cell[0]) / 2,
    (knight.cell[1] + mage.cell[1]) / 2
  )
  return [
    lambda step: (
      setattr(mage, "faction", "ally"),
      game.camera.focus(midpoint, speed=8, force=True),
      mage.face(knight.cell),
      game.anims.append([JumpAnim(target=mage, on_end=step)])
    ),
    lambda step: game.child.open(DialogueContext(script=[
      (mage.name, "OKAY OKAY! Alright. I get it now. I'll come along."),
      (mage.name, "I obviously can't get rid of you, so I submit."),
      lambda: knight.face(mage.cell),
      (knight.name, "I don't have anything to tie you up with,"),
      (knight.name, "so I'm trusting you not to run away."),
    ]), on_close=step),
    lambda step: game.anims.append([ShakeAnim(target=mage, duration=30, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: game.child.open(DialogueContext(script=[
      (mage.name, "Boy are you dumb! But I don't think I will."),
      (mage.name, "My spirit is crushed. I am depressed."),
    ]), on_close=step),
    lambda step: (
      game.camera.focus(add_cell(room.get_edges()[0], (0, 2)), speed=8, force=True),
      game.anims.append([PauseAnim(duration=15, on_end=step)]),
    ),
    lambda step: (
      knight.face(add_cell(knight.cell, (0, -1))),
      step()
    ),
    lambda step: game.child.open(DialogueContext(script=[
      (knight.name, "Now to find a way out of here..."),
      (mage.name, "I am so depressed..."),
    ]), on_close=step),
  ]

def postbattle_cutscene_teardown(room, game):
  mage = room.mage
  return [
    lambda step: (
      game.recruit(mage),
      room.unlock(game),
      game.learn_skill(skill=BroadSword),
      game.end_step(),
      step()
    ),
    lambda step: game.child.open(DialogueContext(
      script=[
        ("", ("Received ", BroadSword().token(), ".")),
      ],
      log=game.log
    ), on_close=step),
  ]
