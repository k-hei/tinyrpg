from math import inf
from random import randint, choice
from dungeon.features.specialroom import SpecialRoom
from dungeon.props.coffin import Coffin
from dungeon.props.vcoffin import VCoffin
from dungeon.actors.mage import Mage
from dungeon.actors.mummy import Mummy
from items.gold import Gold
import lib.vector as vector
from config import ROOM_WIDTHS, ROOM_HEIGHTS, RUN_DURATION

from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from anims.path import PathAnim
from anims.pause import PauseAnim
from anims.jump import JumpAnim
from anims.shake import ShakeAnim
from anims.move import MoveAnim
from anims.warpin import WarpInAnim
from vfx.alertbubble import AlertBubble

class CoffinRoom(SpecialRoom):
  def __init__(room, *args, **kwargs):
    super().__init__(
      shape=["." * 9 for _ in range(7)],
      elems=[
        ((2, 2), coffin1 := Coffin()),
        ((4, 2), Coffin()),
        ((6, 2), Coffin()),
        ((2, 4), Coffin()),
        ((4, 4), coffin2 := Coffin()),
        ((6, 4), coffin3 := Coffin()),
        ((1, 0), VCoffin()),
        ((3, 0), VCoffin()),
        ((5, 0), VCoffin()),
        ((7, 0), VCoffin()),
      ],
      *args, **kwargs
    )
    room.enemy_coffins = [coffin1, coffin2, coffin3]

  def get_edges(room):
    return [
      vector.add(room.cell, (room.get_width() // 2, room.get_height()))
    ]

  def place(room, stage, *args, **kwargs):
    if not super().place(stage, *args, **kwargs):
      return False
    room.mage = stage.spawn_elem_at(vector.add(room.cell, (7, 0)), Mage(faction="ally", facing=(0, -1)))
    return True

  def on_enter(room, game):
    if not super().on_enter(game):
      return False
    game.open(CutsceneContext([
      *cutscene(room, game)
    ]))
    return True

def cutscene(room, game):
  hero = game.hero
  mage = room.mage
  return [
    lambda step: game.anims.append([PauseAnim(duration=15, on_end=step)]),
    lambda step: (
      game.vfx.append(AlertBubble(hero.cell)),
      game.anims.append([PauseAnim(duration=45, on_end=step)]),
    ),
    lambda step: (
      hero.move_to(vector.add(room.cell, (7, 2))),
      game.anims.append([PathAnim(
        target=hero,
        period=RUN_DURATION,
        path=[vector.add(room.cell, c) for c in [(4, 6), (4, 5), (5, 5), (6, 5), (7, 5), (7, 4), (7, 3), (7, 2)]]
      )]),
      game.camera.focus(
        cell=vector.add(room.cell, (7, 2)),
        speed=75,
        tween=True,
        on_end=step
      ),
    ),
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
      move_anim := MoveAnim(target=mage, duration=inf, period=30),
      game.child.open(DialogueContext(script=[
        (mage.get_name().upper(), "Ugh, I'm getting deja vu..."),
        lambda: game.anims.append([JumpAnim(target=hero)]),
        (hero.get_name().upper(), "First you waltz in here without a permit, then you jack my stuff"),
        (hero.get_name().upper(), "and leave my naked ass to get buried alive."),
        (hero.get_name().upper(), "Just how rotten can you get?"),
        lambda: (
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.LaughAnim())
        ) and (mage.get_name().upper(), "Hee hee hee..."),
        lambda: (
          mage.core.anims.clear(),
          game.anims.append([move_anim])
        ) and (mage.get_name().upper(), "You're gonna wish you'd stayed in that rotten old pile of bones!"),
        (hero.get_name().upper(), "????"),
        lambda: (
          move_anim.end(),
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.CastAnim())
        ) and (mage.get_name().upper(), "Hee..."),
        lambda: (
          mage.set_facing((-1, 0)),
          mage.core.anims.clear(),
          mage.core.anims.append(mage.core.YellAnim()),
          game.anims.append([ShakeAnim(target=mage, magnitude=0.5)])
        ) and (mage.get_name().upper(), "HOOOOO!!!!"),
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
      game.vfx.append(AlertBubble(hero.cell)),
      game.child.open(DialogueContext(script=[
        lambda: [
          (
            game.floor.spawn_elem_at(c.cell, mummy := Mummy()),
            game.anims[0].append(WarpInAnim(
              target=mummy,
              duration=15,
              delay=i * 8,
              on_start=c.open
            ))
          ) for i, c in enumerate(room.enemy_coffins)
        ] and ("????", "Urrrrrgh....."),
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
      # mage.move_to(vector.add(room.cell, (room.get_width() // 2, -1))),
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
      game.camera.focus(
        cell=vector.add(room.get_center(), (0, 0.5)),
        speed=15,
        tween=True,
        on_end=step
      ),
    ),
    lambda step: (
      game.child.open(DialogueContext(script=[
        lambda: (
          hero.set_facing((-1, 0)),
          game.anims.append([JumpAnim(target=mage)])
        ) and (hero.get_name().upper(), "Damn! That little...!"),
        (hero.get_name().upper(), "Looks like I'll have to put these guys back to sleep first..."),
        lambda: (
          game.floor_view.stop_shake(),
        ) and None
      ]), on_close=step)
    ),
  ]
