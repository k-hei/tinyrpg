from contexts.app import App
from contexts.explore import ExploreContext
from contexts.explore.manifest import manifest_stage
from contexts.explore.roomdata import load_room

room_data = load_room("rooms/", "debug")
App(
  title="explore context demo",
  context=ExploreContext(
    stage=manifest_stage(room_data)
  )
).init()
