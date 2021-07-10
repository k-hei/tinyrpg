from dungeon.features.specialroom import SpecialRoom
from dungeon.actors.mage import Mage
from dungeon.props.bag import Bag
from skills.weapon.rustyblade import RustyBlade
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from anims.pause import PauseAnim
from anims.drop import DropAnim
from anims.awaken import AwakenAnim
from anims.jump import JumpAnim
from anims.path import PathAnim
from anims.attack import AttackAnim
from anims.item import ItemAnim
from vfx.alertbubble import AlertBubble
from skills.weapon.longinus import Longinus
from lib.cell import add
from config import CUTSCENES

from dungeon.gen import gen_floor
from dungeon.features.room import Room
from dungeon.features.treasureroom import TreasureRoom
from items.hp.potion import Potion

class DepthsRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(degree=1, shape=[
      "#.....#",
      ".......",
      ".......",
      ".......",
      ".......",
      ".......",
      "#.....#"
    ], elems=[
      ((4, 3), mage := Mage(faction="ally")),
      ((2, 2), Bag(RustyBlade)),
    ], *args, **kwargs)
    room.mage = mage
    room.focused = False

  def get_cells(room):
    return [c for c in super().get_cells() if c not in room.get_corners()]

  def get_border(room):
    return super().get_border() + room.get_corners()

  def get_edges(room):
    room_width, room_height = room.get_size()
    room_x, room_y = room.cell or (0, 0)
    return [
      (room_x + room_width // 2, room_y - 2),
      (room_x + room_width // 2, room_y - 1),
    ]

  def on_focus(room, game):
    if room.focused:
      return False
    room.focused = True
    game.hero.cell = add(room.cell, (3, 5))
    game.hero.set_facing((0, -1))
    game.open(CutsceneContext(script=[
      *(cutscene(room, game) if CUTSCENES else [])
    ]))
    return True

  def create_floor(room, *args, **kwargs):
    entry_room = DepthsRoom()
    fork_room = Room(size=(5, 4), degree=3)
    item_room = TreasureRoom(item=Potion)
    return gen_floor(
      entrance=type(entry_room),
      features=[
        [fork_room, entry_room, item_room],
      ]
    )

def cutscene(room, game):
  return [
    lambda step: (
      game.camera.focus(room.get_center()),
      game.anims.extend([
        [
          PauseAnim(duration=30),
          DropAnim(
            target=game.hero,
            on_end=lambda: game.hero.inflict_ailment("sleep")
          ),
          DropAnim(
            target=room.mage,
            delay=30,
            on_end=lambda: room.mage.inflict_ailment("sleep")
          )
        ],
        [PauseAnim(duration=30, on_end=step)]
      ])
    ),
    lambda step: (
      game.camera.focus(room.mage.cell, force=True, speed=8),
      game.anims.append([PauseAnim(duration=30, on_end=step)])
    ),
    lambda step: (
      room.mage.dispel_ailment(),
      game.anims.append([AwakenAnim(target=room.mage, duration=30, on_end=step)])
    ),
    lambda step: game.anims.append([JumpAnim(target=room.mage, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      room.mage.set_facing((-1, 0)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: (
      room.mage.set_facing((0, 1)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: game.child.open(DialogueContext(script=[
      (room.mage.get_name(), "I'm alive...")
    ], on_close=step)),
    lambda step: (
      room.mage.set_facing((0, -1)),
      game.anims.append([PauseAnim(duration=30, on_end=step)])
    ),
    lambda step: (
      room.mage.set_facing((-1, 0)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: (
      game.vfx.append(AlertBubble(cell=room.mage.cell)),
      game.anims.append([PauseAnim(duration=60, on_end=step)])
    ),
    lambda step: (
      room.mage.move_to(add(room.cell, (4, 5))),
      game.camera.focus(add(room. cell, (2.5, 4.5)), force=True, speed=8),
      game.anims.append([PathAnim(
        target=room.mage,
        path=[add(room.cell, c) for c in [(4, 3), (3, 3), (3, 4)]],
        on_end=step
      )])
    ),
    lambda step: (
      room.mage.set_facing((-1, 0)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: game.child.open(DialogueContext(script=[
      (room.mage.get_name(), "Hmmm..."),
      (room.mage.get_name(), "I doubt this son of a gun has two brain cells to rub together, but...")
    ], on_close=step)),
    lambda step: (
      room.mage.set_facing((0, -1)),
      game.anims.append([PauseAnim(duration=30, on_end=step)])
    ),
    lambda step: (
      room.mage.set_facing((0, 1)),
      game.anims.append([PauseAnim(duration=30, on_end=step)])
    ),
    lambda step: (
      room.mage.set_facing((-1, 0)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: game.child.open(DialogueContext(script=[
      (room.mage.get_name(), ". . . . ."),
      (room.mage.get_name(), "...that weapon he's holding doesn't look half bad...")
    ], on_close=step)),
    lambda step: (
      room.mage.set_facing((0, 1)),
      game.anims.append([PauseAnim(duration=45, on_end=step)])
    ),
    lambda step: (
      room.mage.set_facing((-1, 0)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: game.anims.extend([
      [AttackAnim(
        target=room.mage,
        duration=15,
        src=room.mage.cell,
        dest=game.hero.cell,
        on_end=step
      )],
      [ItemAnim(
        target=room.mage,
        duration=15,
        item=Longinus
      )]
    ]),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      game.camera.focus(add(room.cell, (3, 2)), force=True, speed=8),
      room.mage.move_to(add(room.cell, (3, 2))),
      game.anims.append([PathAnim(
        target=room.mage,
        path=[add(room.cell, c) for c in [(3, 4), (3, 3), (3, 2)]],
        on_end=step
      )])
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      room.mage.set_facing((0, 1)),
      game.anims.append([JumpAnim(target=room.mage, on_end=step)])
    ),
    lambda step: game.child.open(DialogueContext(script=[
      (room.mage.get_name(), "Well then!"),
      (room.mage.get_name(), "I'd better make like a tree and get the hell out of here."),
      (room.mage.get_name(), "There's a million places I'd rather be than this godforsaken tomb...")
    ], on_close=step)),
    lambda step: (
      room.mage.set_facing((1, 0)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: (
      room.mage.set_facing((0, -1)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: (
      room.mage.move_to(add(room.cell, (3, -1))),
      game.anims.append([PathAnim(
        target=room.mage,
        path=[add(room.cell, c) for c in [(3, 2), (3, 1), (3, 0), (3, -1)]],
        on_end=step
      )])
    ),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      game.floor.remove_elem(room.mage),
      game.camera.focus(game.hero.cell, force=True, speed=8),
      game.anims.append([PauseAnim(duration=60, on_end=step)])
    ),
    lambda step: (
      game.hero.dispel_ailment(),
      game.anims.append([AwakenAnim(target=game.hero, duration=30, on_end=step)])
    ),
    lambda step: game.anims.append([JumpAnim(target=game.hero, on_end=step)]),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      game.hero.set_facing((1, 0)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    ),
    lambda step: (
      game.hero.set_facing((-1, 0)),
      game.anims.append([PauseAnim(duration=30, on_end=step)])
    ),
    lambda step: (
      game.hero.set_facing((0, 1)),
      game.anims.append([PauseAnim(duration=15, on_end=step)])
    )
  ]
