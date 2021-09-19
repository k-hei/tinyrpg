from dungeon.events.oasisplace import on_place as oasisplace

def resolve_event(key):
  if key == "oasisplace": return oasisplace
