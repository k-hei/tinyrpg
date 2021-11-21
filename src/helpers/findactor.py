from dungeon.actors import DungeonActor

def find_actor(char, stage):
  return next((e for e in stage.elems if
    isinstance(e, DungeonActor)
    and e.core is char
  ), None)
