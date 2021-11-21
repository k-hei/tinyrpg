from contexts.app import App
from contexts.dungeon import DungeonContext
from contexts.explore.manifest import manifest_stage
from contexts.explore.roomdata import load_room
from game.data import GameData
from dungeon.actors.knight import Knight

room_data = load_room("rooms/", "debug")
hero = Knight()
stage = manifest_stage(room_data)
stage_entrance = next((cell for cell, tile in stage.tiles.enumerate() if tile.__name__ == "Exit"), None)
stage_entrance and stage.spawn_elem_at(stage_entrance, hero)

App(
  title="explore context demo",
  context=DungeonContext(
    store=GameData(party=[hero.core]),
    stage=stage,
  )
).init()
