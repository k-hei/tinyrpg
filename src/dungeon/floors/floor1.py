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
from anims.warpin import WarpInAnim
from anims.pause import PauseAnim

class Floor1(Floor):
  def generate(store=None, seed=None):
    return gen_floor(
      features=Graph(
        nodes=[
          entry_room := Room(data=RoomData(**rooms["entry"])),
          exit_room := Room(data=RoomData(**rooms["exit"], doors="RareTreasureDoor")),
          puzzle_room := Room(data=RoomData(**rooms["pzlt1"])),
          buffer_room := Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
            spawns_vases=True,
            degree=2
          )),
          intro_room := Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
            spawns_enemies=[Eyeball(), Eyeball()],
            degree=3,
            hooks={
              "on_enter": lambda room, game: (
                genie_cell := sorted(get_room_bonus_cells(room, game.floor), key=lambda c: manhattan(c, game.hero.cell))[0],
                game.floor.spawn_elem_at(genie_cell, genie := Genie(
                  name=(genie_name := "Joshin"),
                  message=[
                    (genie_name, "It doesn't look like you have a weapon equipped."),
                    (genie_name, "Why don't you try looking around some more?"),
                    (genie_name, "There's bound to be something you can use around here somewhere..."),
                  ]
                )),
                game.anims.append([
                  WarpInAnim(target=genie, delay=30)
                ])
              )
            }
          )),
          key_room := Room(data=RoomData(**rooms["key"])),
          Room(cells=gen_blob(min_area=80, max_area=100), data=RoomData(
            spawns_enemies=[Eyeball(rare=True), Mushroom(), Mushroom()],
            spawns_vases=True,
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
