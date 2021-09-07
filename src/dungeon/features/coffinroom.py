from math import inf
from random import randint, choice
from dungeon.features.specialroom import SpecialRoom
from dungeon.props.coffin import Coffin
from dungeon.props.vcoffin import VCoffin
from dungeon.props.battledoor import BattleDoor
from dungeon.actors import DungeonActor
from dungeon.actors.mage import Mage
from dungeon.actors.mummy import Mummy
from dungeon.actors.beetle import Beetle
from skills.armor.buckler import Buckler
from items.materials.diamond import Diamond
from items.gold import Gold
import lib.vector as vector
import config
from config import (
  ROOM_WIDTHS, ROOM_HEIGHTS,
  RUN_DURATION, PUSH_DURATION, NUDGE_DURATION
)

from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from anims.path import PathAnim
from anims.pause import PauseAnim
from anims.jump import JumpAnim
from anims.shake import ShakeAnim
from anims.move import MoveAnim
from anims.warpin import WarpInAnim
from anims.attack import AttackAnim
from vfx.alertbubble import AlertBubble

class CoffinRoom(SpecialRoom):
  EntryDoor = BattleDoor
  ExitDoor = BattleDoor

  def __init__(room, *args, **kwargs):
    super().__init__(
      degree=4,
      shape=["." * 9 for _ in range(7)],
      elems=[
        ((2, 2), coffin1 := Coffin(Gold(amount=randint(5, 20)))),
        ((4, 2), Coffin(Beetle(), locked=True)),
        ((6, 2), Coffin(Buckler, locked=True)),
        ((2, 4), Coffin(Diamond, locked=True)),
        ((4, 4), coffin2 := Coffin(Gold(amount=randint(5, 20)))),
        ((6, 4), coffin3 := Coffin()),
        ((1, 0), VCoffin()),
        ((3, 0), VCoffin()),
        ((5, 0), VCoffin()),
        ((7, 0), VCoffin()),
      ],
      *args, **kwargs
    )
    room.enemy_coffins = [coffin1, coffin2, coffin3]

  def get_entrances(room):
    return [
      vector.add(room.cell, (room.get_width() // 2 - 1, room.get_height())),
      vector.add(room.cell, (room.get_width() // 2 + 0, room.get_height())),
      vector.add(room.cell, (room.get_width() // 2 + 1, room.get_height())),
      vector.add(room.cell, (room.get_width() // 2 - 1, room.get_height() + 1)),
      vector.add(room.cell, (room.get_width() // 2 + 0, room.get_height() + 1)),
      vector.add(room.cell, (room.get_width() // 2 + 1, room.get_height() + 1)),
    ]

  def get_exits(room):
    return [
      vector.add(room.cell, (room.get_width() // 2, -1)),
      vector.add(room.cell, (-1, room.get_height() // 2)),
      vector.add(room.cell, (room.get_width(), room.get_height() // 2)),
    ]

  def get_enemies(room, stage):
    return [e for e in [
      stage.get_elem_at(c, superclass=DungeonActor) for c in room.get_cells()
    ] if e and e.get_faction() == "enemy"]

  def place(room, stage, *args, **kwargs):
    if not super().place(stage, *args, **kwargs):
      return False
    room.mage = stage.spawn_elem_at(vector.add(room.cell, (7, 0)), Mage(faction="ally", facing=(0, -1)))
    return True

  def unlock(room, game):
    for door in room.get_doors(game.floor):
      door.handle_open(game)

  def lock(room, game):
    for door in room.get_doors(game.floor):
      door.handle_close(game)

  def on_focus(room, game):
    if not super().on_focus(game):
      return False
    for door in room.get_doors(game.floor):
      door.open()
    return True

  def on_enter(room, game):
    if not super().on_enter(game):
      return False
    game.open(CutsceneContext([
      *(cutscene(room, game) if (config.CUTSCENES and "minxia" not in game.store.story) else [
        lambda step: (
          game.floor.remove_elem(room.mage),
          step()
        ),
        *take_battle_position(room, game),
        lambda step: (
          spawn_enemies(room, game),
          room.lock(game),
          step()
        )
      ])
    ]))
    return True

  def on_death(room, game, actor):
    if room.get_enemies(game.floor):
      return False
    game.anims.append([
      PauseAnim(
        duration=30,
        on_end=lambda: room.on_complete(game)
      )
    ])
    return True

  def on_complete(room, game):
    for c, e in room.elems:
      if type(e) is Coffin:
        e.unlock()
    room.unlock(game)

def cutscene(room, game):
  hero = game.hero
  mage = room.mage
  return [
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      game.vfx.append(AlertBubble(hero.cell)),
      game.anims.append([PauseAnim(duration=45, on_end=step)]),
    ),
    *take_battle_position(room, game),
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      game.child.open(DialogueContext(script=[
        lambda: game.anims.append([ShakeAnim(target=mage, duration=15)]),
        (hero.get_name().upper(), "You sure like running, don't you?"),
        lambda: game.anims.append([JumpAnim(target=mage)]),
        (mage.get_name().upper(), "Eep!"),
      ]), on_close=step)
    ),
    lambda step: (
      mage.set_facing((1, 0)),
      game.anims.append([PauseAnim(duration=10, on_end=step)]),
    ),
    lambda step: (
      mage.set_facing((0, 1)),
      game.anims.append([PauseAnim(duration=10, on_end=step)]),
    ),
    lambda step: (
      game.child.open(DialogueContext(script=[
        (mage.get_name().upper(), "Ugh, you AGAIN?"),
        lambda: (
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.CheekyAnim())
        ) and (mage.get_name().upper(), "Look, I already spent all your little coins on jewelry and makeup."),
        (mage.get_name().upper(), "You don't have a reason to chase me!"),
        lambda: (
          game.anims.append([MoveAnim(
            target=hero,
            duration=PUSH_DURATION,
            src=hero.cell,
            dest=vector.add(hero.cell, hero.get_facing()),
          )]),
          hero.move_to(vector.add(hero.cell, hero.get_facing()))
        ) and (hero.get_name().upper(), "Give me my sword."),
        lambda: (
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.LaughAnim())
        ) and (mage.get_name().upper(), "Hee hee hee..."),
        lambda: (
          mage.core.anims.clear(),
          game.anims.append([MoveAnim(target=mage, duration=inf, period=30)])
        ) and (mage.get_name().upper(), "How about I keep it, and you deal with whatever nice fellas might be in here?"),
        (hero.get_name().upper(), "????"),
        lambda: (
          game.anims.clear(),
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.CastAnim())
        ) and (mage.get_name().upper(), "SUPER...."),
        (mage.get_name().upper(), "YELLING..."),
        (mage.get_name().upper(), "ATTACK!!!"),
        lambda: (
          mage.set_facing((-1, 0)),
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.YellAnim()),
          game.anims.append([
            ShakeAnim(target=mage, magnitude=0.5),
            MoveAnim(
              target=hero,
              duration=NUDGE_DURATION,
              src=hero.cell,
              dest=vector.add(hero.cell, (0, 1)),
            )
          ]),
          game.vfx.append(AlertBubble(hero.cell)),
          hero.move_to(vector.add(hero.cell, (0, 1)))
        ) and (mage.get_name().upper(), "AAAAAHHH!!!!!!!!!"),
      ]), on_close=step),
    ),
    lambda step: (
      game.camera.focus(
        cell=vector.add(room.get_center(), (0, 0.5)),
        speed=30,
        tween=True,
        on_end=step
      ),
    ),
    lambda step: (
      game.floor_view.shake(duration=inf, vertical=True),
      hero.set_facing((-1, 0)),
      game.child.open(DialogueContext(script=[
        spawn_enemies(room, game) and ("????", "Urrrrrgh....."),
        lambda: (
          hero.set_facing((0, -1)),
          game.anims[0].append(JumpAnim(target=hero)),
        ) and (hero.get_name().upper(), "You idiot! You're gonna get us both killed!")
      ]), on_close=step)
    ),
    lambda step: (
      game.anims.clear(),
      mage.core.anims.clear(),
      mage.set_facing((0, 1)),
      game.anims.append([MoveAnim(target=mage, duration=inf, period=30)]),
      game.camera.focus(
        cell=vector.add(room.get_center(), (0, -room.get_height() // 2 + 2)),
        speed=15,
        tween=True,
        on_end=step
      ),
    ),
    lambda step: (
      game.child.open(DialogueContext(script=[
        (mage.get_name().upper(), "If someone's gonna kick the bucket down here,"),
        (mage.get_name().upper(), "it's not gonna be me!"),
        (hero.get_name().upper(), "!!"),
      ]), on_close=step),
    ),
    lambda step: (
      mage.move_to(vector.add(room.cell, (4, -1))),
      game.anims.clear(),
      game.anims.append([PathAnim(
        target=mage,
        period=RUN_DURATION,
        path=[vector.add(room.cell, c) for c in [(7, 0), (6, 0), (5, 0), (4, 0), (4, -1)]],
        on_end=step
      )])
    ),
    lambda step: game.anims.append([PauseAnim(duration=30, on_end=step)]),
    lambda step: (
      mage.set_facing((-1, 0)),
      game.anims.append([PauseAnim(duration=5, on_end=step)]),
    ),
    lambda step: (
      mage.set_facing((0, -1)),
      game.anims.append([PauseAnim(duration=5, on_end=step)]),
    ),
    lambda step: (
      mage.set_facing((1, 0)),
      game.anims.append([PauseAnim(duration=5, on_end=step)]),
    ),
    lambda step: (
      mage.set_facing((0, 1)),
      game.anims.append([PauseAnim(duration=5, on_end=step)]),
    ),
    lambda step: game.anims.append([JumpAnim(target=mage, on_end=step)]),
    lambda step: (
      game.child.open(DialogueContext(script=[
        (mage.get_name().upper(), "So long, suckers!"),
        (mage.get_name().upper(), "Don't make too much of a mess, you hear?"),
      ]), on_close=step),
    ),
    lambda step: game.anims.append([PathAnim(
      target=mage,
      period=RUN_DURATION,
      path=[vector.add(room.cell, (room.get_width() // 2, -1), c) for c in [(0, 0), (0, -1)]],
      on_end=lambda: (
        game.floor.remove_elem(mage),
        step()
      )
    )]),
    lambda step: (
      game.child.open(DialogueContext(script=[
        lambda: game.anims.append([ShakeAnim(target=hero, duration=30)]),
        (hero.get_name().upper(), "H-hey!"),
      ]), on_close=step)
    ),
    lambda step: (
      game.anims.clear(),
      game.anims.append([PathAnim(
        target=hero,
        period=RUN_DURATION,
        path=[vector.add(room.cell, c) for c in [(7, 2), (7, 1), (7, 0), (6, 0), (5, 0), (4, 0)]],
        on_end=step
      ), PauseAnim(
        duration=45,
        on_end=lambda: room.lock(game)
      )]),
      hero.move_to(vector.add(room.cell, (4, 0))),
    ),
    lambda step: (
      hero.set_facing((0, -1)),
      game.anims.append([AttackAnim(
        target=hero,
        src=hero.cell,
        dest=vector.add(hero.cell, hero.get_facing()),
        on_end=step
      )])
    ),
    lambda step: (
      game.anims.append([AttackAnim(
        target=hero,
        src=hero.cell,
        dest=vector.add(hero.cell, hero.get_facing()),
        on_end=step
      )])
    ),
    lambda step: (
      game.child.open(DialogueContext(script=[
        lambda: (
          hero.set_facing((-1, 0)),
          game.anims.append([JumpAnim(target=mage)])
        ) and (hero.get_name().upper(), "Damn! That mousy little...!"),
        lambda: (
          hero.set_facing((0, 1))
        ) or (hero.get_name().upper(), "Looks like I'll have to put these guys back to sleep first!"),
        lambda: (
          game.floor_view.stop_shake(),
        ) and None
      ]), on_close=step)
    ),
  ]

def pathfind(start, goal):
  path = [start]
  cell = start
  while cell != goal:
    current_x, current_y = cell
    goal_x, goal_y = goal
    if current_y > goal_y:
      current_y -= 1
    elif current_y < goal_y:
      current_y += 1
    elif current_x > goal_x:
      current_x -= 1
    elif current_x < goal_x:
      current_x += 1
    cell = (current_x, current_y)
    path.append(cell)
  return path

def take_battle_position(room, game):
  hero = game.hero
  return [
    lambda step: (
      game.anims.append([PathAnim(
        target=hero,
        period=RUN_DURATION,
        path=[
          *pathfind(game.hero.cell, vector.add(room.cell, (5, 5))),
          *[vector.add(room.cell, c) for c in [(6, 5), (7, 5), (7, 4), (7, 3), (7, 2)]]
        ]
      )]),
      hero.move_to(vector.add(room.cell, (7, 2))),
      game.camera.focus(
        cell=hero.cell,
        speed=75,
        tween=True,
        on_end=step
      ),
    ),
  ]

def spawn_enemies(room, game):
  return [
    (
      game.floor.spawn_elem_at(c.cell, mummy := Mummy(aggro=1)),
      not game.anims and game.anims.append([]),
      game.anims[0].append(WarpInAnim(
        target=mummy,
        duration=15,
        delay=i * 8,
        on_start=c.open
      ))
    ) for i, c in enumerate(room.enemy_coffins)
  ]
