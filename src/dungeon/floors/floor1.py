from random import randint
from lib.cell import add as add_cell
from dungeon.actors.genie import Genie
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.ghost import Ghost
from dungeon.actors.mummy import Mummy
from dungeon.actors.skeleton import Skeleton
from dungeon.features.room import Room
from dungeon.features.vertroom import VerticalRoom
from dungeon.features.depthsroom import DepthsRoom
from dungeon.features.lockedexitroom import LockedExitRoom
from dungeon.features.itemroom import ItemRoom
from dungeon.features.enemyroom import EnemyRoom
from items.hp.potion import Potion
from items.sp.bread import Bread
from items.ailment.antidote import Antidote
from items.dungeon.emerald import Emerald
from contexts.cutscene import CutsceneContext
from contexts.dialogue import DialogueContext
from anims.flicker import FlickerAnim
from lib.graph import Graph
from dungeon.gen import gen_floor
from dungeon.floors import Floor

class Floor1(Floor):
  scripts = [
    ("equip", lambda game: CutsceneContext(script=[
      lambda step: game.child.open(DialogueContext(script=[
        (game.talkee.name, "Do you have a weapon on you?"),
        (game.talkee.name, "Try pressing 'B' to open up the CUSTOM menu."),
        (game.talkee.name, "You'll be a sitting duck in the dungeon without a weapon equipped."),
      ]), on_close=step),
      lambda step: (
        game.anims.append([FlickerAnim(
          target=game.talkee,
          duration=45,
          on_end=lambda: (
            game.floor.remove_elem(game.talkee),
            step()
          )
        )])
      ),
      lambda step: game.child.open(DialogueContext(script=[
        (game.hero.name, "We have a certain someone to thank for that..."),
      ]), on_close=step)
    ]))
  ]

  def generate(store):
    entry_room = DepthsRoom()
    fork_room = Room(
      size=(5, 4),
      degree=3,
      on_place=lambda room, stage: (
        "minxia" not in store.story and stage.spawn_elem_at(add_cell((room.get_width() - 1, 0), room.cell), Genie(
          name="Joshin",
          message=next((s for s in Floor1.scripts if s[0] == "equip"), None)
        ))
      )
    )
    exit_room = LockedExitRoom()
    lock_room = VerticalRoom(degree=4)
    item_room1 = ItemRoom(size=(3, 4), items=["minxia" in store.story and Emerald or Potion, Bread, *([Antidote] if randint(1, 5) == 1 else [])])
    item_room2 = ItemRoom(size=(5, 4), items=[Potion, Bread, Antidote])
    enemy_room1 = EnemyRoom(size=(5, 4), enemies=[gen_enemy(Eyeball), gen_enemy(Eyeball)])
    enemy_room2 = EnemyRoom(size=(5, 7), enemies=[gen_enemy(Eyeball), gen_enemy(Mushroom), gen_enemy(Mushroom)])
    enemy_room3 = EnemyRoom(size=(3, 4), degree=1, enemies=[gen_enemy(Eyeball, rare=True), gen_enemy(Mushroom), gen_enemy(Ghost)])

    return gen_floor(
      entrance=entry_room,
      features=Graph(
        nodes=[fork_room, entry_room, enemy_room1, item_room1, lock_room, exit_room, enemy_room2, item_room2, enemy_room3],
        edges=[
          (fork_room, entry_room),
          (fork_room, item_room1),
          (fork_room, enemy_room1),
          (lock_room, enemy_room1),
          (lock_room, exit_room),
          (enemy_room2, item_room2),
        ]
      ),
      enemies=[Eyeball, Eyeball, Eyeball, Mushroom, Mushroom, Ghost]
    )
