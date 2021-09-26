from random import randint
from lib.graph import Graph
from lib.cell import manhattan
from dungeon.floors import Floor
from dungeon.room import Blob as Room
from dungeon.roomdata import RoomData, rooms
from dungeon.gen import gen_floor
from dungeon.gen.blob import gen_blob
from dungeon.actors.eyeball import Eyeball
from dungeon.actors.mushroom import Mushroom
from dungeon.actors.genie import Genie
from dungeon.gen.elems import get_room_bonus_cells
from items.hp.potion import Potion
from items.equipment.rustyblade import RustyBlade
from skills.weapon import Weapon
from anims.warpin import WarpInAnim
from anims.flicker import FlickerAnim
from anims.pause import PauseAnim
from comps.log import Token
from colors.palette import GRAY, RED, BLUE

class Floor1(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=Graph(
        nodes=[
          entry_room := Room(data=RoomData(**rooms["entry"])),
          exit_room := Room(data=RoomData(**rooms["exit"], doors="RareTreasureDoor")),
          puzzle_room := Room(data=RoomData(**rooms["pzlt1"])),
          buffer_room := Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
            items=[Potion, RustyBlade],
            degree=2
          )),
          intro_room := Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
            spawns_enemies=[Eyeball(), Eyeball()],
            degree=3,
            hooks={
              "on_enter": lambda room, game: "minxia" not in game.store.story and (
                genie_cell := sorted(get_room_bonus_cells(room, game.floor), key=lambda c: manhattan(c, game.hero.cell))[0],
                game.floor.spawn_elem_at(genie_cell, genie := Genie(
                  name=(genie_name := "Joshin"),
                  message=lambda *_: not next((s for s in game.store.skills if issubclass(s, Weapon)), None) and [
                    (genie_name, "It doesn't look like you have a weapon on you."),
                    (genie_name, "Why don't you try looking around some more?"),
                    (genie_name, "There's bound to be something you can use around here somewhere..."),
                  ] or not next((s for n, b in game.store.builds.items() for s, c in b if n == "Knight" and issubclass(s, Weapon)), None) and [
                    (genie_name, ("You'll need to ", Token(text="equip a weapon", color=GRAY), " before you can use it.")),
                    (genie_name, ("Open ", Token(text="the EQUIP menu", color=BLUE), " with the START button (E).")),
                  ] or [
                    (genie_name, ("Did you know that ", Token(text="attacking from behind", color=RED), " deals extra damage?")),
                    (genie_name, "Try and land a sneak attack!"),
                    lambda: game.anims.append([FlickerAnim(
                      target=genie,
                      duration=30,
                      on_end=lambda: game.floor.remove_elem(genie)
                    )])
                  ]
                )),
                game.anims.append([
                  WarpInAnim(target=genie, delay=15)
                ])
              )
            }
          )),
          key_room := Room(data=RoomData(**rooms["key"])),
          Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
            spawns_enemies=[Eyeball(rare=True), Mushroom(), Mushroom()],
            items=True,
            degree=1,
            secret=True
          )),
        ],
        edges=[
          (entry_room, buffer_room),
          (buffer_room, intro_room),
          (intro_room, exit_room),
          (puzzle_room, key_room),
        ]
      ),
      extra_room_count=4, # 4 + randint(0, 2),
      seed=seed
    )
